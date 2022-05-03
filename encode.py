from PIL import Image
from PIL.ExifTags import TAGS
import numpy as np
import sys
np.set_printoptions(threshold=sys.maxsize)

QOI_HEADER_SIZE = 14
QOI_END_MARKER = [0, 0, 0, 0, 0, 0, 0, 1]
QOI_END_MARKER_SIZE = len(QOI_END_MARKER)

def indexPosition(r, g, b, a):
    return (r * 3 + g * 5 + b * 7 + a * 11) % 64

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
    previousPixel = color(0, 0, 0, 255)
    maxSize = IMG_WIDTH * IMG_HEIGHT * (CHANNELS + 1) + QOI_HEADER_SIZE + QOI_END_MARKER_SIZE
    byteStream = np.uint8(np.zeros(maxSize)) # Worst case encoding
    
    print(img)

# main()