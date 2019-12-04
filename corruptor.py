"""Corrupts a file."""

import getopt
import os
import random  # not for cryptographic use!
import sys

def parse_integer(value, min_, max_, description):
    """Parse integer from command line arguments."""

    try:
        value = int(value, 0)
        if min_ is not None and value < min_:
            raise ValueError
        if max_ is not None and value > max_:
            raise ValueError
    except ValueError:
        sys.exit("Invalid command line integer argument: " + description)
    return value

def get_source_size(source):
    """Get size of source file."""

    if not os.path.isfile(source):
        sys.exit("Input file not found.")
    try:
        fileSize = os.path.getsize(source)
    except OSError:
        sys.exit("Error getting input file size.")
    if fileSize == 0:
        sys.exit("Input file is empty.")
    return fileSize

def create_target_filename(source):
    """Create name for target file from source file. (If an unused filename cannot be found, just
    give up and return the last name we attempted.)"""

    (root, extension) = os.path.splitext(source)
    for n in range(1, 1000 + 1):
        target = "{:s}-corrupt{:d}{:s}".format(root, n, extension)
        if not os.path.exists(target):
            break
    return target

def validate_target_filename(target):
    """Validate name of target file."""

    if os.path.exists(target):
        sys.exit("Output file already exists.")
    dir_ = os.path.dirname(target)
    if dir_ != "" and not os.path.isdir(dir_):
        sys.exit("Output directory not found.")

def parse_command_line_arguments():
    """Parse command line arguments using getopt."""

    shortOpts = "c:m:x:s:l:o:"
    longOpts = (
        "count=", "method=", "xor-value=", "start=", "length=", "output-file="
    )
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], shortOpts, longOpts)
    except getopt.GetoptError:
        sys.exit("Invalid command line argument.")
    opts = dict(opts)

    # method
    method = opts.get("--method", opts.get("-m", "F")).upper()
    if method not in ("F", "I", "D", "R", "X"):
        sys.exit("Invalid command line method argument.")

    # XOR value
    XORValue = opts.get("--xor-value", opts.get("-x", "0xff"))
    XORValue = parse_integer(XORValue, 0x01, 0xff, "XOR value")

    # source file
    if len(args) != 1:
        sys.exit("Invalid number of command line arguments.")
    source = args[0]
    sourceSize = get_source_size(source)

    # start address
    start = opts.get("--start", opts.get("-s", "0"))
    start = parse_integer(start, 0, sourceSize - 1, "start address")

    # length
    length = opts.get("--length", opts.get("-l"))
    if length is None:
        length = sourceSize - start
    else:
        length = parse_integer(length, 1, sourceSize - start, "length")

    # number of bytes to corrupt
    byteCount = opts.get("--count", opts.get("-c", "1"))
    byteCount = parse_integer(byteCount, 1, length, "byte count")

    # target file
    target = opts.get("--output-file", opts.get("-o"))
    if target is None:
        target = create_target_filename(source)
    validate_target_filename(target)

    return {
        "count": byteCount,
        "method": method,
        "XOR": XORValue,
        "start": start,
        "length": length,
        "source": source,
        "target": target,
    }

def pick_addresses(settings):
    """Randomly pick addresses to corrupt. Yield in ascending order."""

    addressRange = range(settings["start"], settings["start"] + settings["length"])
    for address in sorted(random.sample(addressRange, settings["count"])):
        yield address

def read_slice(handle, bytesLeft):
    """Read slice from file, starting from current position.
    Yield one chunk per call."""

    while bytesLeft:
        chunkSize = min(bytesLeft, 2 ** 20)
        yield handle.read(chunkSize)
        bytesLeft -= chunkSize

def copy_slice(source, target, length):
    """Copy slice from one file to another."""

    for chunk in read_slice(source, length):
        target.write(chunk)

def corrupt_byte(byte, method, XORValue):
    """Corrupt one byte."""

    if method == "F":
        # flip random bit (XOR with random power of two)
        return byte ^ (1 << random.randrange(8))
    if method == "I":
        # increment
        return (byte + 1) & 0xff
    if method == "D":
        # decrement
        return (byte - 1) & 0xff
    if method == "R":
        # randomize (any value but the original)
        return random.choice(list(range(byte)) + list(range(byte + 1, 0xff + 1)))
    if method == "X":
        # XOR
        return byte ^ XORValue
    sys.exit("Invalid method.")  # should never happen

def create_line_format(sourceSize):
    """Create format code for printing corrupt bytes."""

    maxAddressLength = len(format(sourceSize - 1, "x"))
    return "0x{{:0{:d}x}}: 0x{{:02x}} -> 0x{{:02x}}".format(maxAddressLength)

def copy_and_corrupt_byte(source, target, settings, lineFormat):
    """Read one byte from one file, corrupt it, write to another file,
    print the change."""

    addr = source.tell()
    origByte = source.read(1)[0]
    corruptByte = corrupt_byte(origByte, settings["method"], settings["XOR"])
    target.write(bytes((corruptByte,)))
    print(lineFormat.format(addr, origByte, corruptByte))

def corrupt_file(source, target, settings):
    """Read input file, write corrupt output file, print changes."""

    sourceSize = source.seek(0, 2)
    lineFormat = create_line_format(sourceSize)
    source.seek(0)
    target.seek(0)

    # for each address to corrupt...
    for address in pick_addresses(settings):
        # copy unchanged data up to but not including corrupt byte
        copy_slice(source, target, address - source.tell())
        # copy and corrupt one byte
        copy_and_corrupt_byte(source, target, settings, lineFormat)
    # copy unchanged data after last corrupt byte
    copy_slice(source, target, sourceSize - source.tell())

def main():
    """The main function."""

    if sys.version_info[0] != 3:
        print("Warning: possibly incompatible Python version.", file=sys.stderr)

    settings = parse_command_line_arguments()

    try:
        with open(settings["source"], "rb") as source, open(settings["target"], "wb") as target:
            corrupt_file(source, target, settings)
    except OSError:
        sys.exit("Error reading/writing files.")

if __name__ == "__main__":
    main()
