import numpy as np
from PIL import Image
QOI_OP_RUN    = 0xc0 # 11xxxxxx
QOI_OP_DIFF   = 0x40 # 01xxxxxx
QOI_OP_INDEX  = 0x00 # 00xxxxxx
QOI_HEADER_SIZE = 14
img = Image.open('imgs/kodim10.png')
IMG_WIDTH = img.width
IMG_HEIGHT = img.height
CHANNELS = len(img.mode)
# 0x716F6966 / "qoif"

class color:
  def __init__(self, r, g, b, a):
    self.r = r
    self.g = g
    self.b = b
    self.a = a

def hashPosition(color):
  return (color.r * 3 + color.g * 5 + color.b * 7 + color.a * 11) % 64

pixel = color(255, 255, 0, 255)

hashPos = hashPosition(pixel)

print(pixel = 
  