import getopt
import os.path
import random  # not for cryptographic use!
import sys

# maximum number of bytes to read from file to RAM at a time
MAX_CHUNK_SIZE = 2 ** 20

def parse_command_line_arguments():
    """Parse command line arguments using getopt."""

    longOpts = ("byte-count=", "method=", "start=", "length=")
    try:
        (opts, args) = getopt.getopt(sys.argv[1:], "b:m:s:l:", longOpts)
    except getopt.GetoptError:
        exit("Error: unrecognized argument. See the readme file.")

    opts = dict(opts)

    # number of bytes to corrupt
    byteCount = opts.get("--byte-count", opts.get("-b", "1"))
    try:
        byteCount = int(byteCount, 0)
    except ValueError:
        exit("Error: number of bytes to corrupt is not an integer.")

    # corruption method
    method = opts.get("--method", opts.get("-m", "FR")).upper()
    if method not in ("FL", "FM", "FA", "FR", "I", "D", "R"):
        exit("Error: invalid corruption method.")

    # start address
    start = opts.get("--start", opts.get("-s", "0"))
    try:
        start = int(start, 0)
    except ValueError:
        exit("Error: start address is not an integer.")

    # length (-1 = default)
    length = opts.get("--length", opts.get("-l", "-1"))
    try:
        length = int(length, 0)
    except ValueError:
        exit("Error: length is not an integer.")

    # files
    if len(args) != 2:
        exit("Error: incorrect number of arguments. See the readme file.")
    (source, target) = args

    # input file
    if not os.path.isfile(source):
        exit("Error: input file not found.")
    try:
        size = os.path.getsize(source)
    except OSError:
        exit("Error getting input file size.")
    if size == 0:
        exit("Error: the file is empty.")

    # validate integer arguments against file size
    if not 0 <= start <= size - 1:
        exit("Error: invalid start address.")
    if length == -1:
        length = size - start
    elif not 1 <= length <= size - start:
        exit("Error: invalid length.")
    if not 1 <= byteCount <= length:
        exit("Error: invalid number of bytes to corrupt.")

    # output file
    if os.path.exists(target):
        exit("Error: target file already exists.")
    targetDir = os.path.dirname(target)
    if targetDir != "" and not os.path.isdir(targetDir):
        exit("Error: target directory not found.")

    return {
        "byteCount": byteCount,
        "method": method,
        "start": start,
        "length": length,
        "source": source,
        "target": target,
    }

def get_addresses_to_corrupt(settings):
    """Yield addresses to corrupt in ascending order."""

    range_ = range(settings["start"], settings["start"] + settings["length"])
    for address in sorted(random.sample(range_, settings["byteCount"])):
        yield address

def read_file(handle, bytesLeft):
    """Read a slice starting from current position in file.
    Generate one chunk per call."""

    while bytesLeft:
        chunkSize = min(bytesLeft, MAX_CHUNK_SIZE)
        yield handle.read(chunkSize)
        bytesLeft -= chunkSize

def corrupt_byte(byte, method):
    if method == "FL":
        return byte ^ 0b0000_0001
    if method == "FM":
        return byte ^ 0b1000_0000
    if method == "FA":
        return byte ^ 0b1111_1111
    if method == "FR":
        bitmask = 1 << random.randrange(8)  # a random power of two
        return byte ^ bitmask
    if method == "I":
        return (byte + 1) % 256
    if method == "D":
        return (byte - 1) % 256
    if method == "R":
        values = set(range(256)) - set(byte)  # any other value
        return random.choice(values)

    exit("Invalid method.")  # should never happen

def generate_corrupt_file(source, settings):
    """Read input file, yield output file in chunks, print changes."""

    fileSize = source.seek(0, 2)
    source.seek(0)

    # maximum length of address in hexadecimal
    maxAddrLen = len(format(settings["start"] + settings["length"] - 1, "x"))
    # line format for printing the changes
    lineFormat = "0x{{:0{:d}x}}: 0x{{:02x}} -> 0x{{:02x}}".format(maxAddrLen)

    for address in get_addresses_to_corrupt(settings):
        # copy unchanged data
        for chunk in read_file(source, address - source.tell()):
            yield chunk
        # corrupt a byte
        oldByte = source.read(1)[0]
        newByte = corrupt_byte(oldByte, settings["method"])
        yield bytes((newByte,))
        # print the change
        print(lineFormat.format(address, oldByte, newByte))

    # copy the last unchanged data
    for chunk in read_file(source, fileSize - source.tell()):
        yield chunk

def main():
    settings = parse_command_line_arguments()

    try:
        with open(settings["source"], "rb") as source, \
        open(settings["target"], "wb") as target:
            target.seek(0)
            for chunk in generate_corrupt_file(source, settings):
                target.write(chunk)
    except OSError:
        exit("File read/write error.")

if __name__ == "__main__":
    main()
