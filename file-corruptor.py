import os.path
import random  # not for cryptographic use!
import sys

HELP_TEXT = """\
File corruptor by Kalle (http://qalle.net)

Corrupts a file. In each randomly-picked byte, one randomly-picked bit will
be flipped. No byte will be corrupted more than once.

Command line arguments:
    SOURCE_FILE TARGET_FILE BYTES_TO_CORRUPT START LENGTH

    SOURCE_FILE
        file to read; required
    TARGET_FILE
        file to write, or a directory to write the file under with its
        original name; either way, the file must not already exist; required
    BYTES_TO_CORRUPT
        number of bytes to corrupt; range: 1...LENGTH;
        optional; default: 1
    START
        never corrupt bytes below address START;
        range: 0 ... (size of SOURCE_FILE) - 1;
        optional; default: 0 (start of file)
    LENGTH
        never corrupt bytes above address START + LENGTH - 1;
        range: 1 ... (size of SOURCE_FILE) - START;
        optional; default: maximum (end of file)

    In other words, the addresses to corrupt will be randomly picked from
    the range START ... START + LENGTH - 1, inclusive, where 0 is the first
    byte of the file. If START and LENGTH are omitted, any address may be
    picked.

    Numeric arguments support the prefix "0x" (hexadecimal).

Examples:
    Read smb.nes, corrupt one byte anywhere, save as corrupt.nes:
        smb.nes corrupt.nes
    Read smb.nes, corrupt 4 bytes between 0x8000...0x8fff, inclusive,
    save as corrupt.nes:
        smb.nes corrupt.nes 4 0x8000 0x1000\
"""

# maximum number of bytes to read from file to RAM at a time
MAX_CHUNK_SIZE = 2**20

BITS_PER_BYTE = 8

def parse_command_line_arguments():
    """Parse command line arguments from sys.argv"""

    if not 3 <= len(sys.argv) <= 6:
        exit(HELP_TEXT)

    return {
        "source": sys.argv[1],
        "target": sys.argv[2],
        "bytesToCorrupt": sys.argv[3] if len(sys.argv) >= 4 else None,
        "start": sys.argv[4] if len(sys.argv) >= 5 else None,
        "length": sys.argv[5] if len(sys.argv) >= 6 else None,
    }

def parse_integer(string):
    """Convert command line argument from str to int."""

    string = string.upper()

    # decode prefix
    if string.startswith("0X"):
        base = 16
        string = string[2:]
    else:
        base = 10

    try:
        return int(string, base)
    except ValueError:
        exit("{:s}: invalid integer".format(string))

def validate_settings(settings):
    """Convert and validate settings."""

    # source path
    if not os.path.isfile(settings["source"]):
        exit("source file does not exist or is not a file")

    # file size needed to validate numeric arguments
    fileSize = os.path.getsize(settings["source"])

    # start position
    if settings["start"] is None:
        settings["start"] = 0
    else:
        settings["start"] = parse_integer(settings["start"])
        if not 0 <= settings["start"] < fileSize:
            exit("invalid start position")

    # length
    if settings["length"] is None:
        settings["length"] = fileSize - settings["start"]
    else:
        settings["length"] = parse_integer(settings["length"])
        if not 1 <= settings["length"] <= fileSize - settings["start"]:
            exit("invalid length")

    # number of bytes to corrupt
    if settings["bytesToCorrupt"] is None:
        settings["bytesToCorrupt"] = 1
    else:
        settings["bytesToCorrupt"] = parse_integer(settings["bytesToCorrupt"])
        if not 1 <= settings["bytesToCorrupt"] <= settings["length"]:
            exit("invalid number of bytes to corrupt")

    # target path
    if os.path.isdir(settings["target"]):
        settings["target"] = os.path.join(settings["target"], os.path.basename(settings["source"]))
    if os.path.isfile(settings["target"]):
        exit("target file already exists")

    return settings

def pick_random_addresses(settings):
    """Pick addresses to corrupt (must be sorted)."""

    range_ = range(settings["start"], settings["start"] + settings["length"])
    return sorted(random.sample(range_, settings["bytesToCorrupt"]))

def copy_chunk_unchanged(source, bytesLeft, target):
    """Copy bytesLeft bytes unchanged from source to target in chunks of
    1...MAX_CHUNK_SIZE bytes."""

    while bytesLeft:
        chunkSize = min(bytesLeft, MAX_CHUNK_SIZE)
        bytesLeft -= chunkSize
        target.write(source.read(chunkSize))

def corrupt_byte(source, target):
    """Read one byte from source, corrupt, write to target."""

    address = source.tell()
    oldByte = source.read(1)[0]
    # flip a random bit (XOR with a random power of two)
    newByte = oldByte ^ (1 << random.randrange(BITS_PER_BYTE))
    target.write(bytes((newByte,)))
    print("0x{:08x}: 0x{:02x} -> 0x{:02x}".format(address, oldByte, newByte))

def corrupt_file(source, target, settings):
    """Copy source to target, corrupting bytes on the way."""

    addressesToCorrupt = pick_random_addresses(settings)

    fileSize = source.seek(0, 2)
    source.seek(0)
    target.seek(0)

    # process file as alternating unchanged chunks and corrupted bytes
    for addr in addressesToCorrupt:
        copy_chunk_unchanged(source, addr - source.tell(), target)
        corrupt_byte(source, target)
    copy_chunk_unchanged(source, fileSize - source.tell(), target)

def main():
    settings = parse_command_line_arguments()
    settings = validate_settings(settings)

    try:
        with open(settings["source"], "rb") as source:
            try:
                with open(settings["target"], "wb") as target:
                    corrupt_file(source, target, settings)
            except OSError:
                exit("write error")
    except OSError:
        exit("read error")

if __name__ == "__main__":
    main()
