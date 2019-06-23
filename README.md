# file-corruptor
Makes a corrupt copy of a file. The bytes to corrupt will be randomly picked from the specified address range. Works well with large files. Good for romhacks, pranks (**at your own risk**), etc.

Developed with Python 3 under 64-bit Windows.

## Command line arguments

Syntax: [*options*] *input_file*

Integer arguments support hexadecimal values with the prefix `0x` (e.g. `0xff` = 255).

### *options*

* `-c` *count* or `--count`=*count*
  * The number of bytes to corrupt.
  * *count* is an integer:
    * minimum: 1
    * default: 1
    * maximum: same as *length* (see below)
* `-m` *method* or `--method`=*method*
  * How to corrupt (change) each byte.
  * *method* is one of the following (case insensitive):
    * `F`: flip one randomly-selected bit (the default; e.g. `0x00` &rarr; `0x80`/`0x40`/etc.)
    * `I`: increment (add one; `0xff` overflows to `0x00`)
    * `D`: decrement (subtract one; `0x00` underflows to `0xff`)
    * `R`: randomize (replace with any value but the original)
    * `X`: XOR the byte with a constant (see `-x`)
* `-x` *value* or `--xor-value`=*value*
  * The constant to XOR each byte with.
  * Has no effect with *method*s other than `X`.
  * *value* is an integer:
    * minimum: `0x00`
    * default: `0xff`
    * maximum: `0xff`
* `-s` *start* or `--start`=*start*
  * The start of the address range where the bytes to corrupt will be picked from.
  * *start* is an integer:
    * minimum: 0 (the first byte of the file)
    * default: 0
    * maximum: size of *input_file* in bytes, minus one
* `-l` *length* or `--length`=*length*
  * The length of the address range where the bytes to corrupt will be picked from.
  * *length* is an integer:
    * minimum: 1
    * default: size of *input_file* in bytes, minus *start*
    * maximum: size of *input_file* in bytes, minus *start*
* `-o` *file* or `--output-file`=*file*
  * The file to write.
  * The file must not already exist (it will not be overwritten).
  * Default: input file name with `-corrupt#` inserted before the extension, where `#` is the first integer between 0 and 999 that results in a nonexistent file (e.g. `smb.nes` &rarr; `smb-corrupt0.nes`, `smb-corrupt1.nes`, etc.).

With default `-s` and `-l`, the addresses to corrupt will be picked from anywhere in the file.

### *input_file*
* The file to read.
* Required.

## Examples

Read `smb.nes`, corrupt one byte anywhere by flipping a randomly selected bit, save as `smb-corrupt0.nes` (or `smb-corrupt1.nes` if it already exists, etc.):

```
python corruptor.py smb.nes
0x63df: 0x08 -> 0x48
```

Read `smb.nes`, corrupt 5 bytes between `0x2010`&ndash;`0x300f`, inclusive, by flipping the most significant bits, save as `corrupt.nes`:

```
python corruptor.py -c 5 -m x -x 0x80 -s 0x2010 -l 0x1000 -o corrupt.nes smb.nes
0x263b: 0xdc -> 0x5c
0x2879: 0xf9 -> 0x79
0x2a94: 0x00 -> 0x80
0x2aea: 0xd9 -> 0x59
0x2dec: 0x47 -> 0xc7
```
