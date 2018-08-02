import ssl
import hashlib
import ctypes
import readline
import dbm
import _gdbm
import lzma
import zlib


def main():
    # hopefully, even the oldest ca-certificates will verify node js npm registry
    from urllib import request
    response = request.urlopen("https://registry.npmjs.org/")
    assert(response.getcode() == 200)


if __name__ == "__main__":
    main()
