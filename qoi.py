# Import modules
from PIL import Image
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

# Declare constant variables
MAGIC = 0x716F6966 # "qoif" in hexadecimal
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
  bytes[index] = (value & 0xff000000) >> 24 
  index+=1
  bytes[index] = (value & 0x00ff0000) >> 16 
  index+=1
  bytes[index] = (value & 0x0000ff00) >> 8 
  index+=1
  bytes[index] = (value & 0x000000ff) >> 0 
  index+=1

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
  write32(byteStream, MAGIC)
  write32(byteStream, IMG_WIDTH)
  write32(byteStream, IMG_HEIGHT)
  byteStream[index] = CHANNELS
  index += 1 
  byteStream[index] = 1 # All channels linear
  index += 1 

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

def writeFile(data):
  f = open("image.qoi", "wb")
  f.write(data)
  f.close()

def decode(qoi_path):
  qoi = open(qoi_path, "rb").read()
  MAGIC = qoi[0:4]
  IMG_WIDTH = int.from_bytes(qoi[4:8], "big")
  IMG_HEIGHT = int.from_bytes(qoi[8:12], "big")
  CHANNELS = qoi[12]

  if MAGIC != b'qoif':
    print(f'{qoi_path} is not a .qoi image.')
    return 

  seenPixels = np.full(64, color(0, 0, 0, 0))
  size = IMG_WIDTH * IMG_HEIGHT
  pixels = np.uint8(np.zeros(shape=(size, CHANNELS)))
  index = 14
  px_pos = 0
  run = 0

  while True:
    byteTag = qoi[index]        # 8bit tag
    bitTag = qoi[index] & 0xc0  # 2bit tag

    # Check for end tag
    # if (np.frombuffer(qoi[index:index+QOI_END_MARKER_SIZE], dtype=np.uint8) == QOI_END_MARKER).all():
    #   break
    if px_pos == size:
      break
    
    if byteTag == QOI_OP_RGB:
      pixel = color(qoi[index+1], qoi[index+2], qoi[index+3], 255)
      index += 4

    elif byteTag == QOI_OP_RGBA:
      pixel = color(qoi[index+1], qoi[index+2], qoi[index+3], qoi[index+4])
      index += 5

    elif bitTag == QOI_OP_RUN:
      run = (qoi[index] & 0x3f) + 1
      if px_pos == 0:
        pixel = color(0, 0, 0, 255)
      elif CHANNELS == 3:
        pixel = color(
          pixels[px_pos-1][0],
          pixels[px_pos-1][1],
          pixels[px_pos-1][2],
          255)   
      elif CHANNELS == 4:
        pixel = color(
          pixels[px_pos-1][0],
          pixels[px_pos-1][1],
          pixels[px_pos-1][2],
          pixels[px_pos-1][3]
          )
      index += 1

    elif bitTag == QOI_OP_INDEX:
      hashPos = qoi[index] & 0x3F
      pixel = seenPixels[hashPos]
      index += 1

    elif bitTag == QOI_OP_DIFF:
      dr, dg, db = qoi[index] & 0x30, qoi[index] & 0x0c, qoi[index] & 0x03
      r, g, b = pixels[px_pos-1][0] + dr, pixels[px_pos-1][1] + dg, pixels[px_pos-1][2] + db
      if CHANNELS == 4:
        a = pixels[px_pos][3]
      else:
        a = 255
      pixel = color(r, g, b, a)
      index += 1
      
    elif bitTag == QOI_OP_LUMA:
      # dg = qoi[index] & 0x3f - 32
      # dr_dg = ((qoi[index + 1] & 0xF0) >> 4) - 8
      # db_dg = (qoi[index + 1] & 0x0F) - 8
      # r = pixels[-1][0] - dg
      # g = 0
      # b = 0
      # if CHANNELS == 4:
      #   a = pixels[px_pos-1][3]
      # else:
      #   a = 255
      # pixel = color(r, g, b, a)
      pixel = color(0, 0, 0, 255)
      index += 2

    r, g, b, a = pixel.r, pixel.g, pixel.b, pixel.a 
    if run > 0:
      while run > 0:
        pixels[px_pos][0] = r
        pixels[px_pos][1] = g
        pixels[px_pos][2] = b
        if CHANNELS == 4:
          pixels[px_pos][3] = a 
        px_pos += 1
        run -= 1

    pixels[px_pos][0] = r 
    pixels[px_pos][1] = g
    pixels[px_pos][2] = b
    if CHANNELS == 4:
      pixels[px_pos][3] = a 

    seenPixels[hashPosition(pixel)] = pixel
    px_pos += 1
    
  return pixels.reshape(IMG_HEIGHT, IMG_WIDTH, CHANNELS)  

def main():
  # img_path = 'imgs/kodim23.png'
  # qoi = encode(img_path)
  # writeFile(qoi)
  data = decode("imgs/kodim10.qoi")
  img = Image.fromarray(data, 'RGB')
  img.show()

if __name__ == "__main__":
  main()