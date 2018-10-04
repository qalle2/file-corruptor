# file-corruptor
A file corruptor in Python. Works well with large files.

Developed with Python 3 under 64-bit Windows.

## Command line arguments

Syntax: [*options*] *source_file* *target_file*

Integer arguments support hexadecimal values with the prefix `0x` (e.g. `0xff` = 255).

### *options*

#### `-b` *count* or `--byte-count`=*count*
*count* is the number of bytes to corrupt:
* minimum: 1
* default: 1
* maximum: same as *length* (see below)

No byte (address) will be corrupted more than once.

#### `-m` *method* or `--method`=*method*
*method* is how to corrupt each byte:
* `FL`: flip the least significant bit
* `FM`: flip the most significant bit
* `FA`: flip all bits
* `FR`: flip a random bit (the default)
* `I`: increment
* `D`: decrement
* `R`: randomize

This argument is case insensitive.

#### `-s` *start* or `--start`=*start* and `-l` *length* or `--length`=*length*
The addresses to corrupt will be randomly picked from the range *start* to *start* + *length* - 1, inclusive.

*start* is an integer:
* minimum: 0 (the first byte of the file)
* default: 0
* maximum: file size minus one

*length* is an integer:
* minimum: 1
* default: file size minus *start*
* maximum: file size minus *start*

With the default values, any address may be corrupted.

### *source_file*
The file to read.

### *target_file*
The file to write. The file must not already exist (it will not be overwritten).

## Examples

Read `smb.nes`, corrupt one byte anywhere, save as `corrupt.nes`:

```
C:\>python corruptor.py smb.nes corrupt.nes
0x37d6: 0x04 -> 0x84
```

Read `smb.nes`, corrupt 8 bytes between `0x8010`&ndash;`0x8fff`, inclusive, by flipping all their bits, save as `corrupt.nes`:

```
C:\>python corruptor.py -b 8 -m fa -s 0x8010 -l 0x1000 smb.nes corrupt.nes
0x806e: 0x03 -> 0xfc
0x8280: 0xff -> 0x00
0x84b1: 0xff -> 0x00
0x89e6: 0x38 -> 0xc7
0x8a80: 0x77 -> 0x88
0x8e03: 0x88 -> 0x77
0x8eb8: 0x2f -> 0xd0
0x8ee9: 0x10 -> 0xef
```
