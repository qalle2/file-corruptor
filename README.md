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
