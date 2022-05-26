# Import modules
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

def hashPosition(color):
  return (color.r * 3 + color.g * 5 + color.b * 7 + color.a * 11) % 64

def isEqual(color1, color2):
  return color1.r == color2.r and color1.g == color2.g and color1.b == color2.b and color1.a == color2.a

def difference(color1, color2):
  return color(
    int(color1.r)-int(color2.r),
    int(color1.g)-int(color2.g),
    int(color1.b)-int(color2.b),
    int(color1.a)-int(color2.a),
  )

def write32(bytes, value):
  global index
  bytes[index+0] = (value & 0xff000000) >> 24 
  bytes[index+1] = (value & 0x00ff0000) >> 16 
  bytes[index+2] = (value & 0x0000ff00) >> 8 
  bytes[index+3] = (value & 0x000000ff) >> 0 
  index+=4

def write8(bytes, value):
  global index
  bytes[index] = value
  index+=1

def read32(bytes):
  global readIndex
  a = (bytes[readIndex+0])
  b = (bytes[readIndex+1])
  c = (bytes[readIndex+2])
  d = (bytes[readIndex+3])
  readIndex+=4
  return a << 24 | b << 16 | c << 8 | d

def read8(bytes):
  global readIndex
  a = bytes[readIndex]
  readIndex += 1
  return a

def writePixel(pixels, color, index, CHANNELS):
  pixels[index+0] = color.r
  pixels[index+1] = color.g
  pixels[index+2] = color.b
  if CHANNELS == 4:
    pixels[index+3] = color.a

class color:
  def __init__(self, r, g, b, a):
    self.r = r
    self.g = g
    self.b = b
    self.a = a

def encode(image):
  img = Image.open(image)
  IMG_WIDTH = img.width
  IMG_HEIGHT = img.height
  CHANNELS = len(img.mode)
  imgData = np.uint8(img).flatten()

  seenPixels = np.full(64, color(0, 0, 0, 0))
  prevPixel = color(0, 0, 0, 255)
  pixel = prevPixel
  maxSize = IMG_WIDTH * IMG_HEIGHT * (CHANNELS + 1) + QOI_HEADER_SIZE + QOI_END_MARKER_SIZE # Worst case encoding
  byteStream = np.uint8(np.zeros(maxSize))
  run = 0
  global index
  index = 0

  # Write header
  write32(byteStream, QOI_MAGIC)
  write32(byteStream, IMG_WIDTH)
  write32(byteStream, IMG_HEIGHT)
  write8(byteStream, CHANNELS)
  write8(byteStream, 1) # All channels linear

  for i in range(0, len(imgData), CHANNELS):
    prevPixel = pixel

    pixel = color(
      imgData[i + 0],
      imgData[i + 1],
      imgData[i + 2],
      prevPixel.a
    )

    if CHANNELS == 4:
      pixel.a = imgData[i + 3]
    
    # Run-length operation
    if isEqual(prevPixel, pixel):
      run += 1
      if run == 62 or i == len(imgData) - CHANNELS:
        byteStream[index] = QOI_OP_RUN | run-1
        index += 1
        run = 0
      continue
    else: 
      if run > 0:
        byteStream[index] = QOI_OP_RUN | run-1
        index += 1
        run = 0

    # Index operation
    hashPos = hashPosition(pixel)
    if isEqual(pixel, seenPixels[hashPos]):
      byteStream[index] = QOI_OP_INDEX | hashPos
      index += 1
      continue
    else:
      seenPixels[hashPos] = pixel

    # Difference operation & Luma difference operation
    diff = difference(pixel, prevPixel)
    if diff.a == 0:
      if -2 <= diff.r <= 1 and -2 <= diff.g <= 1 and -2 <= diff.b <= 1:
        byteStream[index] = QOI_OP_DIFF | (diff.r + 2) << 4 | (diff.g + 2) << 2 | (diff.b + 2) << 0
        index += 1
        continue
      if -32 <= diff.g <= 31:
        dr = diff.r - diff.g
        db = diff.b - diff.g
        if -8 <= dr <= 7 and -8 <= db <= 7:
          byteStream[index:index+2] = [QOI_OP_LUMA | (diff.g + 32), (dr + 8) << 4| (db + 8) << 0]
          index += 2
          continue

    # Full RGB(A) operation
    if CHANNELS == 3:
      byteStream[index:index+4] = [QOI_OP_RGB, pixel.r, pixel.g, pixel.b]
      index += 4
      continue
    elif CHANNELS == 4:
      byteStream[index:index+5] = [QOI_OP_RGBA, pixel.r, pixel.g, pixel.b, pixel.a]
      index += 5
      continue

  byteStream[index:index+8] = QOI_END_MARKER[0:8]
  index += 8
  return byteStream[0:index]

def writeFile(data, fileName):
  f = open(fileName, "wb")
  f.write(data)
  f.close()

def decode(qoi_path):
  qoi = open(qoi_path, "rb").read()
 
  global readIndex
  readIndex = 0
  
  # Read header
  MAGIC       = read32(qoi)
  IMG_WIDTH   = read32(qoi)
  IMG_HEIGHT  = read32(qoi)
  CHANNELS    = read8(qoi)
  COLORSPACE  = read8(qoi)

  print(f'MAGIC:      {MAGIC}')
  print(f'WIDTH:      {IMG_WIDTH}')
  print(f'HEIGHT:     {IMG_HEIGHT}')
  print(f'CHANNELS:   {CHANNELS}')

  if MAGIC != QOI_MAGIC or 3 > CHANNELS > 4 or IMG_WIDTH == 0 or IMG_HEIGHT == 0:
    raise Exception("Invalid .qoi file")

  seenPixels = np.full(64, color(0, 0, 0, 0))
  size = IMG_WIDTH * IMG_HEIGHT * CHANNELS
  pixels = np.uint8(np.zeros(size))
  pixel = color(0, 0, 0, 255)
  run = 0

  for writeIndex in range(0, size, CHANNELS):
    if run > 0:
      run -= 1
    else:
      byte = read8(qoi)

      if byte == QOI_OP_RGB:
        pixel.r = read8(qoi)
        pixel.g = read8(qoi)
        pixel.b = read8(qoi)
      
      elif byte == QOI_OP_RGBA:
        pixel.r = read8(qoi)
        pixel.g = read8(qoi)
        pixel.b = read8(qoi)
        pixel.a = read8(qoi)

      elif byte & 0xc0 == QOI_OP_RUN:
        run = byte & 0x3f

      elif byte & 0xc0 == QOI_OP_INDEX:
        pixel = seenPixels[byte & 0x3f]

      elif byte & 0xc0 == QOI_OP_DIFF:
        dr = ((byte >> 4) & 0x03) - 2
        dg = ((byte >> 2) & 0x03) - 2
        db = ((byte >> 0) & 0x03) - 2
        pixel.r += dr 
        pixel.g += dg
        pixel.b += db

      elif byte & 0xc0 == QOI_OP_LUMA:
        byte2 = read8(qoi)
        dg = (byte & 0x3f) - 32
        dr_dg = ((byte2 >> 4) & 0x0f) - 8
        db_dg = ((byte2 >> 0) & 0x0f) - 8
        pixel.r += dg + dr_dg
        pixel.g += dg
        pixel.b += dg + db_dg

      seenPixels[hashPosition(pixel)] = pixel
    writePixel(pixels, pixel, writeIndex, CHANNELS)
  
  return pixels.reshape(IMG_HEIGHT, IMG_WIDTH, CHANNELS)  

def main():
  # img_path = 'imgs/kodim10.png'
  # qoi = encode(img_path)
  # writeFile(qoi, "encodedImage")
  data = decode("imgs/kodim10.qoi")
  img = Image.fromarray(data, 'RGB')
  img.save("decodedImage.png")
  img.show()

if __name__ == "__main__":
  main()