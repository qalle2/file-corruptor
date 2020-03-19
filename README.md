# file-corruptor
```
usage: corruptor.py [-h] [-c COUNT] [-m {f,i,a,r}] [-s START] [-l LENGTH] input_file output_file

Make a corrupt copy of a file. The addresses to corrupt will be randomly picked from the specified range (by default,
from the entire file).

positional arguments:
  input_file            The file to read.
  output_file           The file to write.

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        How many bytes to corrupt. (default: 1)
  -m {f,i,a,r}, --method {f,i,a,r}
                        How to corrupt each byte: f=flip one of the bits; i=invert all bits, a=add or subtract one
                        (255<->0), r=randomize (any value but the original). (default: f)
  -s START, --start START
                        The start of the range to pick addresses from (0=first byte). (default: 0)
  -l LENGTH, --length LENGTH
                        The length of the range to pick addresses from (0=to the end of the file). (default: 0)
```

## Example
Read `smb.nes`, corrupt 4 bytes between `0x2000`-`0x20ff` by inverting all bits, save as `corrupt.nes`:
`python corruptor.py --count 4 --method i --start 8192 --length 256 smb.nes corrupt.nes`
