"""Make a corrupt copy of a file."""

import argparse
import os
import random  # not for cryptographic use!
import sys

def parse_command_line_arguments():
    """Parse command line arguments using argparse."""

    parser = argparse.ArgumentParser(
        description="Make a corrupt copy of a file. The addresses to corrupt will be randomly "
        "picked from the specified range (by default, from the entire file).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument("-c", "--count", type=int, default=1, help="How many bytes to corrupt.")
    parser.add_argument(
        "-m", "--method", choices=("f", "i", "a", "r"), default="f",
        help="How to corrupt each byte: f=flip one of the bits; i=invert all bits, a=add or "
        "subtract one (255<->0), r=randomize (any value but the original)."
    )
    parser.add_argument(
        "-s", "--start", type=int, default=0,
        help="The start of the range to pick addresses from (0=first byte)."
    )
    parser.add_argument(
        "-l", "--length", type=int, default=0,
        help="The length of the range to pick addresses from (0=to the end of the file)."
    )
    parser.add_argument(
        "input_file", help="The file to read."
    )
    parser.add_argument(
        "output_file", help="The file to write."
    )

    args = parser.parse_args()

    if args.count < 1:
        sys.exit("Number of bytes must be one or greater.")
    if args.start < 0:
        sys.exit("Start of address range must be zero or greater.")
    if args.length < 0:
        sys.exit("Length of address range must be zero or greater.")
    if not os.path.isfile(args.input_file):
        sys.exit("Input file not found.")
    if os.path.exists(args.output_file):
        sys.exit("Output file already exists.")

    return args

def copy_file_slice(source, target, bytesLeft):
    """Copy a slice from one file to another."""

    while bytesLeft:
        chunkSize = min(bytesLeft, 2 ** 20)
        target.write(source.read(chunkSize))
        bytesLeft -= chunkSize

def corrupt_byte(byte, method):
    """Corrupt a byte."""

    if method == "f":
        return byte ^ (1 << random.randrange(8))  # flip one bit (XOR with a power of two)
    if method == "i":
        return byte ^ 0xff  # invert all bits
    if method == "a":
        return (byte + random.choice((-1, 1))) % 256  # add/subtract one
    if method == "r":
        return random.choice(list(set(range(256)) - set((byte,))))  # randomize
    assert False  # should never happen
    return None  # for pylint

def corrupt_file(source, target, settings):
    """Read input file, write corrupt output file, print changes."""

    # get file size and range length; further validate the range
    fileSize = source.seek(0, 2)
    rangeLength = settings.length if settings.length else fileSize - settings.start
    if rangeLength < 1 or settings.start + rangeLength > fileSize:
        sys.exit("Invalid address range.")
    if settings.count > rangeLength:
        sys.exit("Too many bytes to corrupt.")

    source.seek(0)
    target.seek(0)

    # pick addresses to corrupt
    addresses = range(settings.start, settings.start + rangeLength)
    for address in sorted(random.sample(addresses, settings.count)):
        # copy unchanged bytes before the address
        copy_file_slice(source, target, address - source.tell())
        # copy and corrupt the byte
        byte = corrupt_byte(source.read(1)[0], settings.method)
        target.write(bytes((byte,)))
    # copy unchanged bytes after the last corrupt byte
    copy_file_slice(source, target, fileSize - source.tell())

def main():
    """The main function."""

    settings = parse_command_line_arguments()
    try:
        with open(settings.input_file, "rb") as source, open(settings.output_file, "wb") as target:
            corrupt_file(source, target, settings)
    except OSError:
        sys.exit("Error reading/writing files.")

if __name__ == "__main__":
    main()
