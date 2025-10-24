# -*- coding: utf-8 -*-
import random
import time
from hashlib import md5

BASE62 = "PJArHa0dpwhvMNYqKnTbitWfEmosQ9527ZBx46IXUgOzD81VuSFyckLRljG3eC"
BASE64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"


def RandomString(_l, chars=BASE62):
    # Generates random string of `len` chars within a selected number of chars
    return "".join([random.choice(chars) for i in range(0, _l)])


def HexDigest(data: bytearray):
    # Digests a `bytearray` to a hex string
    return "".join([hex(d)[2:].zfill(2) for d in data])


def HexCompose(hexstr: str):
    # Composes a hex string back to a `bytearray`
    return bytearray([int(hexstr[i : i + 2], 16) for i in range(0, len(hexstr), 2)])


def HashDigest(text):
    # Digests 128 bit md5 hash
    HASH = md5(text.encode("utf-8"))
    return HASH.digest()


def HashHexDigest(text):
    """Digests 128 bit md5 hash,then digest it as a hexstring"""
    return HexDigest(HashDigest(text))

def GenerateSDeviceId() -> str:
    """Generate sDeviceId
    
    This code is from web source code
    """
    random_num = random.randrange(1000000)
    return f"unknown-{random_num}"

def GenerateChainId(s_device_id: str) -> str:
    """Generate chainId param for web login api
    
    This code is from web source code
    """
    timestamp = int(time.time() * 1000)
    # the rule is "{version}_{s_device_id}_{platform}_{action}_{timestamp}"
    return f"v1_{s_device_id}_web_login_{timestamp}"

def GenerateWNMCID() -> str:
    """Generate WNMCID for cookies
    
    This code is from web source code
    """
    prefix = ''.join(random.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(6))
    timestamp = int(time.time() * 1000)
    crawler_version = "01"
    return f"{prefix}.{timestamp}.{crawler_version}.0"