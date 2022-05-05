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

def difference(color1, color2):
  return color(
    int(color1.r)-int(color2.r),
    int(color1.g)-int(color2.g),
    int(color1.b)-int(color2.b),
    int(color1.a)-int(color2.a),
  )

diff = difference(color(10, 1, 12, 255), color(9, 2, 14, 255))
if -2 <= diff.r <= 1 and -2 <= diff.g <= 1 and -2 <= diff.b <= 1:
    print(diff.r)
    print(diff.g)
    print(diff.b)
    print(diff.a)
    
# test = -3
# if -2 <= test <= 1:
#     print("test")

# print(np.uint8(-2))