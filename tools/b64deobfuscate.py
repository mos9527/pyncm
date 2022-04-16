"""Decrypts(?) obfuscated strings enforced by `a.auu.c` seen in Android version of the app"""

import base64, code


def xor(arr: bytearray, key=b"Encrypt"):
    return bytearray([c ^ key[idx % len(key)] for idx, c in enumerate(arr)])


def decrypt(s: str):
    return xor(base64.b64decode(s)).decode()


def encrypt(s: str):
    return base64.b64encode(xor(s.encode())).decode()


code.interact(local=locals())
