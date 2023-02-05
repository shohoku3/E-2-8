import binascii
import os


if __name__ == '__main__':
    r = os.urandom(16)
    print(r)
    print(type(r))
    rhex = binascii.hexlify(r)
    print(rhex)
    print(int(rhex, 16))
    print((int(rhex, 16) % 1000))