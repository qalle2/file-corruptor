# file-corruptor
A file corruptor in Python. Works well with large files.

Developed with Python 3 under 64-bit Windows.

## Command line arguments

[*options*] *source_file* *target_file*

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

Integer arguments support hexadecimal values with the prefix "0x".

## Examples

Read `smb.nes`, corrupt one byte anywhere, save as `corrupt.nes`:

`python file-corruptor.py smb.nes corrupt.nes`

Read `smb.nes`, corrupt 4 bytes between 0x8000...0x8fff, inclusive, save as `corrupt.nes`:

`python ??? smb.nes corrupt.nes 4`
