# Import modules
from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

MAGIC = 0x716F6966 # "qoif" joined in hexadecimal
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
  # ADD WRAP-AROUND OP?
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
    # print("\n")

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

def decode(qoi_path):
  qoi = open(qoi_path, "rb").read()
  IMG_WIDTH = qoi[4:8]
  IMG_HEIGHT = qoi[8:12]
  print(IMG_WIDTH)
  print(IMG_HEIGHT)

def writeFile(data):
  f = open("image.qoi", "wb")
  f.write(data)
  f.close()

# img_path = 'imgs/kodim23.png'
# qoi = encode(img_path)
# writeFile(qoi)
decode("image.qoi")