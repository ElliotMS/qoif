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

# pixels = np.uint8(np.zeros(10))
# print(pixels[2:6])

test = np.array([1, 2, 3, 4, 5, 6])
test2 = np.array([1, 2, 3, 4, 5, 6])

print((test == test2).all())