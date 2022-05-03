import numpy as np

class color:
  def __init__(self, r, g, b, a):
    self.r = r
    self.g = g
    self.b = b
    self.a = a

seenPixels = np.full(64, color(0, 0, 0, 0))

print(seenPixels)