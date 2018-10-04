# file-corruptor
Makes a corrupt copy of a file. Works well with large files. Good for romhacks, pranks (**at your own risk**), etc.

Developed with Python 3 under 64-bit Windows.

## Command line arguments

Syntax: [*options*] *input_file* *output_file*

Integer arguments support hexadecimal values with the prefix `0x` (e.g. `0xff` = 255).

### *options*

* `-b` *count* or `--byte-count`=*count*
  * The number of bytes to corrupt.
  * *count* is an integer:
    * minimum: 1
    * default: 1
    * maximum: same as *length* (see below)
* `-m` *method* or `--method`=*method*
  * How to corrupt each byte.
  * *method* is one of the following (case insensitive):
    * `FL`: flip the least significant bit (XOR with `0x01`)
    * `FM`: flip the most significant bit (XOR with `0x80`)
    * `FA`: flip all bits (XOR with `0xff`)
    * `FR`: flip a random bit (the default)
    * `I`: increment (add one)
    * `D`: decrement (subtract one)
    * `R`: randomize (replace with any value but the original)
* `-s` *start* or `--start`=*start* and `-l` *length* or `--length`=*length*
  * Define the range where the addresses to corrupt will be picked.
  * The range is *start* to *start* + *length* &minus; 1, inclusive.
  * *start* is an integer:
    * minimum: 0 (the first byte of the file)
    * default: 0
    * maximum: size of *input_file* &minus; 1
  * *length* is an integer:
    * minimum: 1
    * default: size of *input_file* &minus; *start*
    * maximum: size of *input_file* &minus; *start*

### *input_file*
* The file to read.

### *output_file*
* The file to write.
* The file must not already exist (it will not be overwritten).

## Examples

Read `smb.nes`, corrupt one byte anywhere, save as `corrupt.nes`:

```
C:\>python corruptor.py smb.nes corrupt.nes
0x37d6: 0x04 -> 0x84
```

Read `smb.nes`, corrupt 8 bytes between `0x9010`&ndash;`0x980f`, inclusive, by flipping all bits, save as `corrupt.nes`:

```
C:\>python corruptor.py -b 8 -m fa -s 0x9010 -l 0x800 smb.nes corrupt.nes
0x90af: 0x00 -> 0xff
0x9100: 0xfe -> 0x01
0x9165: 0x60 -> 0x9f
0x922c: 0x00 -> 0xff
0x9240: 0xfe -> 0x01
0x9338: 0x00 -> 0xff
0x9410: 0xfe -> 0x01
0x9694: 0x3c -> 0xc3
```
