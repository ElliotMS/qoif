from copy import deepcopy
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
  
class copyColor(color):
    pass

pixel = color(120, 120, 92, 255)
print(pixel.__dict__)
copy = deepcopy(pixel)
print(copy.__dict__)
pixel.r = 100
print(copy.__dict__)



