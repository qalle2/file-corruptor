import getopt
import os.path
import random  # not for cryptographic use!
import sys

# maximum number of bytes to read from file to RAM at a time
MAX_CHUNK_SIZE = 1 << 20

# for getopt
SHORT_OPTS = "c:m:x:s:l:o:"
LONG_OPTS = (
    "count=", "method=", "xor-value=", "start=", "length=", "output-file="
)

# the maximum value of a byte
BYTE_MAX = 0xff

def parse_command_line_arguments():
    """Parse command line arguments using getopt."""

    try:
        (opts, args) = getopt.getopt(sys.argv[1:], SHORT_OPTS, LONG_OPTS)
    except getopt.GetoptError:
        exit("Error: unrecognized argument. See the readme file.")

    opts = dict(opts)

    # number of bytes to corrupt
    byteCount = opts.get("--count", opts.get("-c", "1"))
    try:
        byteCount = int(byteCount, 0)
    except ValueError:
        exit("Error: byte count is not an integer.")

    # method
    method = opts.get("--method", opts.get("-m", "F")).upper()
    if method not in ("F", "I", "D", "R", "X"):
        exit("Error: invalid method.")

    # XOR value
    XORValue = opts.get("--xor-value", opts.get("-x", "0xff"))
    try:
        XORValue = int(XORValue, 0)
        if not 0x00 <= XORValue <= 0xff:
            raise ValueError
    except ValueError:
        exit("Error: invalid XOR value.")

    # start address (validated later)
    start = opts.get("--start", opts.get("-s", "0"))
    try:
        start = int(start, 0)
    except ValueError:
        exit("Error: start address is not an integer.")

    # length (None = default, validated later)
    length = opts.get("--length", opts.get("-l"))
    if length is not None:
        try:
            length = int(length, 0)
        except ValueError:
            exit("Error: length is not an integer.")

    # input file
    if len(args) != 1:
        exit("Error: incorrect number of arguments. See the readme file.")
    source = args[0]

    # input file must exist
    if not os.path.isfile(source):
        exit("Error: input file not found.")

    # get input file size
    try:
        size = os.path.getsize(source)
    except OSError:
        exit("Error getting input file size.")

    # input file must not be empty
    if size == 0:
        exit("Error: the input file is empty.")

    # validate start address against input file size
    if not 0 <= start < size:
        exit("Error: invalid start address.")

    # use default length or validate it against input file size
    if length is None:
        length = size - start
    elif not 0 < length <= size - start:
        exit("Error: invalid length.")

    # validate number of bytes to corrupt against input file size
    if not 1 <= byteCount <= length:
        exit("Error: invalid number of bytes to corrupt.")

    # output file (if unspecified, get nonexistent default name)
    target = opts.get("--output-file", opts.get("-o"))
    if target is None:
        (root, ext) = os.path.splitext(source)
        for i in range(1000):
            target = "{:s}-corrupt{:d}{:s}".format(root, i, ext)
            if not os.path.exists(target):
                break

    # output file must not exist
    if os.path.exists(target):
        exit("Error: target file already exists.")

    # output directory must exist
    dir = os.path.dirname(target)
    if dir != "" and not os.path.isdir(dir):
        exit("Error: target directory not found.")

    return {
        "count": byteCount,
        "method": method,
        "XORValue": XORValue,
        "start": start,
        "length": length,
        "source": source,
        "target": target,
    }

def pick_addresses(opts):
    """Randomly pick addresses to corrupt. Yield in ascending order."""

    range_ = range(opts["start"], opts["start"] + opts["length"])
    addresses = random.sample(range_, opts["count"])
    for address in sorted(addresses):
        yield address

def read_slice(handle, bytesLeft):
    """Read slice from file, starting from current position.
    Yield one chunk per call."""

    while bytesLeft:
        chunkSize = min(bytesLeft, MAX_CHUNK_SIZE)
        yield handle.read(chunkSize)
        bytesLeft -= chunkSize

def copy_slice(source, target, length):
    """Copy slice from one file to another."""

    for chunk in read_slice(source, length):
        target.write(chunk)

def corrupt_byte(byte, method, XORValue):
    """Corrupt one byte."""

    if method == "F":
        # flip one randomly-selected bit (XOR with random power of two)
        return byte ^ (1 << random.randrange(8))
    if method == "I":
        # increment
        return (byte + 1) & BYTE_MAX
    if method == "D":
        # decrement
        return (byte - 1) & BYTE_MAX
    if method == "R":
        # randomize (any value but the original)
        values = list(range(byte)) + list(range(byte + 1, BYTE_MAX + 1))
        return random.choice(values)
    if method == "X":
        # XOR
        return byte ^ XORValue

    exit("Invalid method.")  # should never happen

def copy_and_corrupt_byte(source, target, opts):
    """Read one byte from one file, corrupt it, write to another file,
    print the change."""

    addr = source.tell()
    origByte = source.read(1)[0]
    corruptByte = corrupt_byte(origByte, opts["method"], opts["XORValue"])
    target.write(bytes((corruptByte,)))

    print("0x{:04x}: 0x{:02x} -> 0x{:02x}".format(addr, origByte, corruptByte))

def corrupt_file(source, target, opts):
    """Read input file, write corrupt output file, print changes."""

    fileSize = source.seek(0, 2)
    source.seek(0)
    target.seek(0)

    # for each address to corrupt...
    for address in pick_addresses(opts):
        # copy unchanged data up to but not including corrupt byte
        copy_slice(source, target, address - source.tell())
        # corrupt one byte
        copy_and_corrupt_byte(source, target, opts)

    # copy unchanged data after last corrupt byte
    copy_slice(source, target, fileSize - source.tell())

def main():
    opts = parse_command_line_arguments()

    try:
        with open(opts["source"], "rb") as source, \
        open(opts["target"], "wb") as target:
            corrupt_file(source, target, opts)
    except OSError:
        exit("File read/write error.")

if __name__ == "__main__":
    main()
