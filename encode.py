from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

MAGIC = bytes("qoif", 'utf-8')
QOI_HEADER_SIZE = 14
QOI_END_MARKER = np.uint8([0, 0, 0, 0, 0, 0, 0, 1])
QOI_END_MARKER_SIZE = len(QOI_END_MARKER)

QOI_OP_INDEX  = 0x00 # 00xxxxxx 
QOI_OP_DIFF   = 0x40 # 01xxxxxx
QOI_OP_LUMA   = 0x80 # 10xxxxxx
QOI_OP_RUN    = 0xc0 # 11xxxxxx
QOI_OP_RGB    = 0xfe # 11111110
QOI_OP_RGBA   = 0xff # 11111111

def indexPosition(r, g, b, a):
  return (r * 3 + g * 5 + b * 7 + a * 11) % 64

def isEqual(color1, color2):
  return color1.r == color2.r and color1.g == color2.g and color1.b == color2.b and color1.a == color2.a

class color:
  def __init__(self, r, g, b, a):
    self.r = r
    self.g = g
    self.b = b
    self.a = a

def main():
  img = Image.open('imgs/kodim10.png')
  IMG_WIDTH = img.width
  IMG_HEIGHT = img.height
  CHANNELS = len(img.mode)
  img = np.uint8(img).flatten()

  seenPixels = np.full(64, color(0, 0, 0, 0))
  prevPixel = color(0, 0, 0, 255)
  maxSize = IMG_WIDTH * IMG_HEIGHT * (CHANNELS + 1) + QOI_HEADER_SIZE + QOI_END_MARKER_SIZE
  byteStream = bytearray(maxSize) # Worst case encoding
  run = 0
  index = 0

  for i in range(0, len(img), CHANNELS):
    pixel = color(
      img[i + 0],
      img[i + 1],
      img[i + 2],
      None
    )

    if CHANNELS == 4:
      pixel.a = img[i + 3]

    if isEqual(prevPixel, pixel):
      run += 1
      if run == 62:
          index += 1
          byteStream[index] = QOI_OP_RUN | run
          run = 0
      else:
        continue

    if run > 0:
      index += 1
      byteStream[index] = QOI_OP_RUN | run
      run = 0

    index += 1

    prevPixel = pixel

main()