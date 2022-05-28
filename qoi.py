# Import modules
from copy import deepcopy
from PIL import Image
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

# Declare constant variables
QOI_MAGIC = 0x716F6966 # "qoif" in hexadecimal
QOI_HEADER_SIZE = 14 
QOI_END_MARKER = np.uint8([0, 0, 0, 0, 0, 0, 0, 1])
QOI_END_MARKER_SIZE = len(QOI_END_MARKER)
QOI_OP_INDEX  = 0x00 # 00xxxxxx 
QOI_OP_DIFF   = 0x40 # 01xxxxxx
QOI_OP_LUMA   = 0x80 # 10xxxxxx
QOI_OP_RUN    = 0xc0 # 11xxxxxx
QOI_OP_RGB    = 0xfe # 11111110
QOI_OP_RGBA   = 0xff # 11111111
QOI_MASK_1    = 0xc0 # 11000000
QOI_MASK_2    = 0x3f # 00111111
QOI_MASK_DR   = 0x30 # 00110000
QOI_MASK_DG   = 0x0c # 00001100
QOI_MASK_DB   = 0x03 # 00000011
QOI_MASK_DRDG = 0xf0 # 11110000
QOI_MASK_DBDG = 0x0f # 00001111

class color:
  def __init__(self, r, g, b, a):
    self.r = r
    self.g = g
    self.b = b
    self.a = a

def hashPosition(color):
  # Takes a color object and returns an index (0-63) used in seenPixels[] for both encoder and decoder. Hash function given in qoi-specifications.
  return (color.r * 3 + color.g * 5 + color.b * 7 + color.a * 11) % 64

def isEqual(color1, color2):
  # Takes two colors and returns boolean True/False if they are equal/not equal. 
  return color1.r == color2.r and color1.g == color2.g and color1.b == color2.b and color1.a == color2.a

def difference(color1, color2):
  # Takes two colors and returns color object with the difference of each (r, g, b, a) values of original colors.  
  return color(
    int(color1.r)-int(color2.r),
    int(color1.g)-int(color2.g),
    int(color1.b)-int(color2.b),
    int(color1.a)-int(color2.a),
  )

def write32(bytes, value):
  # Writes 32bit number of given value to given byte array and updates write index.
  global writeIndex
  bytes[writeIndex+0] = (value & 0xff000000) >> 24 
  bytes[writeIndex+1] = (value & 0x00ff0000) >> 16 
  bytes[writeIndex+2] = (value & 0x0000ff00) >> 8 
  bytes[writeIndex+3] = (value & 0x000000ff) >> 0 
  writeIndex+=4

def write8(bytes, value):
  # Writes 32bit number of given value to given byte array and updates write index.
  global writeIndex
  bytes[writeIndex] = value
  writeIndex+=1

def read32(bytes):
  # Reads 32bit number at current readIndex. Returns read value and updates readIndex.
  global readIndex
  a = (bytes[readIndex+0])
  b = (bytes[readIndex+1])
  c = (bytes[readIndex+2])
  d = (bytes[readIndex+3])
  readIndex+=4
  return a << 24 | b << 16 | c << 8 | d

def read8(bytes):
  # Reads 8bit number at current readIndex. Returns read value and updates readIndex.
  global readIndex
  a = bytes[readIndex]
  readIndex += 1
  return a

def writePixel(pixels, color, index, CHANNELS):
  # Writes given color object to pixels array at current writeIndex. 
  pixels[index+0] = color.r
  pixels[index+1] = color.g
  pixels[index+2] = color.b
  if CHANNELS == 4:
    pixels[index+3] = color.a

def writeFile(data, fileName):
  # Writes .qoi data to file of given file name.
  f = open(fileName, "wb")
  f.write(data)
  f.close()

def encode(img_path):
 # Encodes image at given path.
  img = Image.open(img_path)
  IMG_WIDTH = img.width
  IMG_HEIGHT = img.height
  CHANNELS = len(img.mode)
  imgData = np.uint8(img).flatten()

  seenPixels = np.full(64, color(0, 0, 0, 0)) # Zero initialized according to specifications
  prevPixel = color(0, 0, 0, 255) # Previous pixel starts as 0, 0, 0, 255 according to specifications
  maxSize = IMG_WIDTH * IMG_HEIGHT * (CHANNELS + 1) + QOI_HEADER_SIZE + QOI_END_MARKER_SIZE # Worst case encoding
  byteStream = np.uint8(np.zeros(maxSize)) # Create array with maxsize as np.uint8 is non mutable so .append() is invalid.
  run = 0
  global writeIndex
  writeIndex = 0

  # Write header
  write32(byteStream, QOI_MAGIC)
  write32(byteStream, IMG_WIDTH)
  write32(byteStream, IMG_HEIGHT)
  write8(byteStream, CHANNELS)
  write8(byteStream, 1) # All channels linear

  for readIndex in range(0, len(imgData), CHANNELS):

    pixel = color(
      imgData[readIndex + 0],
      imgData[readIndex + 1],
      imgData[readIndex + 2],
      prevPixel.a
    )
    if CHANNELS == 4:
      pixel.a = imgData[readIndex + 3]

    # Run-length operation
    if isEqual(prevPixel, pixel):
      run += 1
      if run == 62 or readIndex == len(imgData) - CHANNELS:
        # If run is max size (62 as b111110 and b111111 are occupied by QOI_OP_RGB and QOI_OP_RGBA) or pixel is last pixel write immediatly.
        byteStream[writeIndex] = QOI_OP_RUN | run-1 # Run is written with bias of -1 as run length can't be lower than 1 so run 0 is uneccecary. 
        writeIndex += 1
        run = 0
        # --> end of loop

    else:

      if run > 0:
        # If current pixel is not a run and we have an active run write immediatly.
        byteStream[writeIndex] = QOI_OP_RUN | run-1 # Run is written with bias of -1 as run length can't be lower than 1 so run 0 is uneccecary. 
        writeIndex += 1
        run = 0

      hashPos = hashPosition(pixel)

      # Index operation
      if isEqual(pixel, seenPixels[hashPos]):
        # If current pixel has been seen previously write as QOI_OP_INDEX.
        byteStream[writeIndex] = QOI_OP_INDEX | hashPos
        writeIndex += 1
        # --> end of loop
      else:
        # Add pixel to previously seen pixels.
        seenPixels[hashPos] = pixel

        # Difference operation & Luma difference operation
        diff = difference(pixel, prevPixel)
        if diff.a == 0:
          # Can only preform QOI_OP_DIFF or QOI_OP_LUMA if difference in alpha values is 0.
          if -2 <= diff.r <= 1 and -2 <= diff.g <= 1 and -2 <= diff.b <= 1:
            # If difference for RGB channels are in range -2 <= x <= 1 write as QOI_OP_DIFF
            byteStream[writeIndex] = QOI_OP_DIFF | (diff.r + 2) << 4 | (diff.g + 2) << 2 | (diff.b + 2) << 0 # Written with bias of 2 to avoid negative int
            writeIndex += 1
            # --> end of loop

          elif -32 <= diff.g <= 31 and -8 <= (diff.r - diff.g) <= 7 and -8 <= (diff.b - diff.g) <= 7:
            # If difference in green channel is in range -32 <= x <= 31 calculate (dr-dg) and (db-dg)             # If difference in (dr-dg) and (db-dg) is in range -8 <= x <= 7 write as QOI_OP_LUMA
            dr_dg = diff.r - diff.g
            db_dg = diff.b - diff.g
            byteStream[writeIndex:writeIndex+2] = [QOI_OP_LUMA | (diff.g + 32), (dr_dg + 8) << 4| (db_dg + 8) << 0] # Written with bias of 32 for diff.g and 8 for dr_dg and db_dg to avoid negative int
            writeIndex += 2
            # --> end of loop

          # Full RGB operation
          else:
            # We know the difference in alpha channel is 0 so we can encode as RGB
            byteStream[writeIndex:writeIndex+4] = [QOI_OP_RGB, pixel.r, pixel.g, pixel.b]
            writeIndex += 4
            # --> end of loop
        
        # Full RGBA operation
        else:
            byteStream[writeIndex:writeIndex+5] = [QOI_OP_RGBA, pixel.r, pixel.g, pixel.b, pixel.a]
            writeIndex += 5
            # --> end of loop
    
    prevPixel = pixel

  byteStream[writeIndex:writeIndex+8] = QOI_END_MARKER[0:8] # Write end marker
  writeIndex += 8
  return byteStream[0:writeIndex] # Return everythingup until end marker

def decode(qoi_path):
  # Decode .qoi file at given path
  qoi = open(qoi_path, "rb").read()

  global readIndex
  readIndex = 0
  
  # Read header
  MAGIC       = read32(qoi)
  IMG_WIDTH   = read32(qoi)
  IMG_HEIGHT  = read32(qoi)
  CHANNELS    = read8(qoi)
  COLORSPACE  = read8(qoi)

  if MAGIC != QOI_MAGIC or 3 > CHANNELS > 4 or IMG_WIDTH == 0 or IMG_HEIGHT == 0:
    # Make sure file is valid .qoi file.
    raise Exception("Invalid .qoi file")

  seenPixels = np.full(64, color(0, 0, 0, 0)) # Zero initialized according to specifications.
  size = IMG_WIDTH * IMG_HEIGHT * CHANNELS 
  pixels = np.uint8(np.zeros(size)) # Create array of right size as np.uint8 is non mutable so .append() is invalid.
  pixel = color(0, 0, 0, 255) # Previous pixel starts as 0, 0, 0, 255 according to specifications.
  run = 0

  for writeIndex in range(0, size, CHANNELS):
    if run > 0:
      # If run is active write pixel immediatly
      run -= 1
    else:
      byte = read8(qoi)

      if byte == QOI_OP_RGB:
        # If RGB operation set r, g, b to next 3 bytes. Alpha remains unchanged.
        pixel.r = read8(qoi)
        pixel.g = read8(qoi)
        pixel.b = read8(qoi)
      
      elif byte == QOI_OP_RGBA:
        # If RGB operation set r, g, b, a to next 4 bytes 
        pixel.r = read8(qoi)
        pixel.g = read8(qoi)
        pixel.b = read8(qoi)
        pixel.a = read8(qoi)

      elif byte & QOI_MASK_1 == QOI_OP_RUN:
        run = (byte & QOI_MASK_2) # Reads last 6 bits.

      elif byte & QOI_MASK_1 == QOI_OP_INDEX:
        index = byte & QOI_MASK_2 # Reads last 6 bits
        pixel = seenPixels[index]

      elif byte & QOI_MASK_1 == QOI_OP_DIFF:
        dr = ((byte & QOI_MASK_DR) >> 4) - 2 # XXxxXXXX > 000000xx
        dg = ((byte & QOI_MASK_DG) >> 2) - 2 # XXXXxxXX > 000000xx
        db = ((byte & QOI_MASK_DB) >> 0) - 2 # XXXXXXxx > 000000xx
        pixel.r = (pixel.r + dr) & 0xff      #                                                                 255         1          256         0xff        0
        pixel.g = (pixel.g + dg) & 0xff      # Use & 0xff to compensate for python not having unsigned ints. 11111111 + 00000001 = 1 00000000 & 11111111 = 00000000. Also works for 0 - 1 = 255.
        pixel.b = (pixel.b + db) & 0xff      # 

      elif byte & QOI_MASK_1 == QOI_OP_LUMA:
        byte2 = read8(qoi)
        dg = (byte & QOI_MASK_2) - 32              # Reads last 6 bits. Reverse +32 bias set in encoding.
        dr_dg = ((byte2 & QOI_MASK_DRDG) >> 4) - 8 # XXXXxxxx > 0000xxxx. Reverse +8 bias set in encoding.
        db_dg = ((byte2 & QOI_MASK_DBDG) >> 0) - 8 # XXXXxxxx > 0000xxxx. Reverse +8 bias set in encoding.
        pixel.r = (pixel.r + dg + dr_dg) & 0xff    #                                                                  0          1            256         0xff       255 
        pixel.g = (pixel.g + dg)         & 0xff    # Use & 0xff to compensate for python not having unsigned ints. 00000000 - 00000001 = ...1 1111111 & 11111111 = 11111111. Also works for 255 + 1 = 0.
        pixel.b = (pixel.b + dg + db_dg) & 0xff    #

      seenPixels[hashPosition(pixel)] = deepcopy(pixel) # Write copy of pixel object to seen pixels. Needs to be copy so color in seenpixels[] doesn't change in future loops. 

    writePixel(pixels, pixel, writeIndex, CHANNELS)

  return pixels.reshape(IMG_HEIGHT, IMG_WIDTH, CHANNELS)

def main():
  # CLI: py qoi.py -encode/-decode img_path
  cmds = [cmd for cmd in sys.argv[1:] if cmd.startswith("-")]
  args = [cmd for cmd in sys.argv[1:] if not cmd.startswith("-")]
  if "-encode" in cmds:
    writeFile(encode(args[0]), "encoded_image.qoi")
  elif "-decode" in cmds:
    img = Image.fromarray(decode(args[0]))
    img.save("decoded_image.png")
  else:
    raise Exception("Command not recognized")

if __name__ == "__main__":
  main()