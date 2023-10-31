# QOIF
Simple implementation of the [Quite OK Image format](https://qoiformat.org/) in Python 3.10.2.

"QOI is fast. It losslessy compresses images to a similar size of PNG, while offering 20x-50x faster encoding and 3x-4x faster decoding."

## Requirements
* Python 3.10.2+
* [NumPy](https://numpy.org/)
* [Pillow](https://pillow.readthedocs.io/en/stable/)

## Usage

```
py qoi.py -command argument
```

Where the command is either:

```-encode```or ```-decode```

And the argument is the absolute or relative image path.

Example:

```
py qoi.py -encode resources/test_images/clover.png
```
