"""Make a corrupt copy of a file."""

import argparse
import os
import random  # not for cryptographic use!
import sys

def parse_args():
    """Parse command line arguments using argparse."""

    parser = argparse.ArgumentParser(
        description="Make a corrupt copy of a file. The addresses to corrupt will be randomly "
        "picked from the specified range (by default, from the entire file).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument(
        "-c", "--count", type=int, default=1, help="Number of bytes to corrupt."
    )
    parser.add_argument(
        "-m", "--method", choices=("f", "i", "a", "r"), default="f",
        help="How to corrupt a byte: f = flip 1 bit, i = invert all bits, a = add or subtract 1 "
        "(255 <-> 0), r = randomize (any value but original)."
    )
    parser.add_argument(
        "-s", "--start", type=int, default=0,
        help="Start of range to pick addresses from (0 or greater)."
    )
    parser.add_argument(
        "-l", "--length", type=int, default=0,
        help="Length of range to pick addresses from (0 = to end of file)."
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Print changes."
    )
    parser.add_argument(
        "input_file", help="The file to read."
    )
    parser.add_argument(
        "output_file", help="The file to write."
    )

    args = parser.parse_args()

    # validate file args
    if not os.path.isfile(args.input_file):
        sys.exit("Input file not found.")
    try:
        fileSize = os.path.getsize(args.input_file)
    except OSError:
        sys.exit("Could not get input file size.")
    if fileSize == 0:
        sys.exit("Input file is empty.")
    if os.path.exists(args.output_file):
        sys.exit("Output file already exists.")

    # validate integer args
    if not 0 <= args.start < fileSize:
        sys.exit("Address range start must be 0 to (file size - 1).")
    if not 0 <= args.length <= fileSize - args.start:
        sys.exit("Address range length must be 0 to (file size - address range start).")
    if not 1 <= args.count <= (args.length if args.length else fileSize - args.start):
        sys.exit("Number of bytes to corrupt must be 1 to (address range length).")

    return args

def corrupt_file(source, target, args):
    """Read input file, write corrupt output file, print changes."""

    def flip_bit(byte):
        return byte ^ (1 << random.randrange(8))  # flip one bit

    def invert_byte(byte):
        return byte ^ 0xff  # invert all bits

    def add_sub(byte):
        return (byte + random.choice((-1, 1))) & 0xff  # add or subtract one

    def randomize(byte):
        return random.choice(list(set(range(0x100)) - set((byte,))))  # any but original

    def copy_slice(source, target, bytesLeft):
        """Copy a slice from one file to another."""

        while bytesLeft:
            chunkSize = min(bytesLeft, 2 ** 20)
            target.write(source.read(chunkSize))
            bytesLeft -= chunkSize

    corruptorFunction = {
        "f": flip_bit,
        "i": invert_byte,
        "a": add_sub,
        "r": randomize,
    }[args.method]

    fileSize = source.seek(0, 2)
    addrRange = range(args.start, args.start + args.length if args.length else fileSize)
    source.seek(0)
    target.seek(0)

    # pick addresses to corrupt
    for address in sorted(random.sample(addrRange, args.count)):
        # copy unchanged bytes before address
        copy_slice(source, target, address - source.tell())
        # copy and corrupt one byte
        origByte = source.read(1)[0]
        corruptByte = corruptorFunction(origByte)
        if args.verbose:
            print(f"0x{address:04x}: 0x{origByte:02x} -> 0x{corruptByte:02x}")
        target.write(bytes((corruptByte,)))
    # copy unchanged bytes after last corrupt byte
    copy_slice(source, target, fileSize - source.tell())

def main():
    """The main function."""

    args = parse_args()
    try:
        with open(args.input_file, "rb") as source, \
        open(args.output_file, "wb") as target:
            corrupt_file(source, target, args)
    except OSError:
        sys.exit("Error reading/writing files.")

if __name__ == "__main__":
    main()

