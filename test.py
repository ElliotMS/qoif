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

array = [1, 2, 3, 4, 5, 6, 7, 8]
print(array[0:-1])

    