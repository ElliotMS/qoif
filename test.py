import numpy as np
QOI_OP_RUN    = 0xc0 # 11xxxxxx
QOI_OP_DIFF   = 0x40 # 01xxxxxx
QOI_OP_INDEX  = 0x00 # 00xxxxxx

byteStream = bytearray(100)
# byteStream[0] = QOI_OP_RUN | 0x60
byteStream[0] = QOI_OP_DIFF | 0x1 | 0x2 | 0x0
byteStream[1] = QOI_OP_INDEX | 0x10
print(format(byteStream[0], '#010b'))
print(format(byteStream[1], '#010b'))
print(byteStream)