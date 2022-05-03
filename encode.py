from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

img = Image.open('imgs/testcard.png')

IMG_WIDTH = img.width
IMG_HEIGHT = img.height
CHANNELS = len(img.mode)

img = np.uintc(img).flatten()

def indexPosition(r, g, b, a):
    return (r * 3 + g * 5 + b * 7 + a * 11) % 64

def QOI_OP_RGB():
    return

def QOI_OP_RGBA():
    return

def QOI_OP_INDEX():
    return

def QOI_OP_DIFF():
    return

def QOI_OP_LUMA():
    return

def QOI_OP_RUN():
    return

class color:
  def __init__(self, r, g, b, a):
    self.r = r
    self.g = g
    self.b = b
    self.a = a

def main():
    seenPixels = np.full(64, color(0, 0, 0, 0))
    previousPixel = color(0, 0, 0, 0)

main()