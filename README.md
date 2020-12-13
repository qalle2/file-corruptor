# file-corruptor
```
usage: corruptor.py [-h] [-c COUNT] [-m {f,i,a,r}] [-s START] [-l LENGTH] [-v]
                    input_file output_file

Make a corrupt copy of a file. The addresses to corrupt will be randomly
picked from the specified range (by default, from the entire file).

positional arguments:
  input_file            The file to read.
  output_file           The file to write.

optional arguments:
  -h, --help            show this help message and exit
  -c COUNT, --count COUNT
                        Number of bytes to corrupt. (default: 1)
  -m {f,i,a,r}, --method {f,i,a,r}
                        How to corrupt a byte: f = flip 1 bit, i = invert all
                        bits, a = add or subtract 1 (255 <-> 0), r = randomize
                        (any value but original). (default: f)
  -s START, --start START
                        Start of range to pick addresses from (0 or greater).
                        (default: 0)
  -l LENGTH, --length LENGTH
                        Length of range to pick addresses from (0 = to end of
                        file). (default: 0)
  -v, --verbose         Print changes. (default: False)
```

