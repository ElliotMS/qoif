<h1>Python QOI-format</h1>
<p>Simple implementation of the <a href="https://qoiformat.org/">Quite OK Image format</a> in Python 3.10.2.</p>
<p>"QOI is fast. It losslessy compresses images to a similar size of PNG, while offering 20x-50x faster encoding and 3x-4x faster decoding."</p>

<h2>Command line interface (CLI)</h2>

```
py qoi.py -command argument
```
<p>Where the command is either:
  
  ```-encode```
  or ```-decode```
</p>

<p>And the argument is the absolute or relative image path.</p>
<p>Example: </p>

```
py qoi.py -encode resources/test_images/clover.png
```
