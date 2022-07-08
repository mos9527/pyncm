# -*- coding: utf-8 -*-
"""Essential implementations of some of netease's security algorithms"""
import base64
from . import HexCompose,HexDigest,HashHexDigest,RandomString,security
from .aes import AES
# region secrets
WEAPI_RSA_PUBKEY = (
    int("00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7",16),
    int("10001",16) # textbook rsa without padding
)
# AES keys & IVs targets AES-128 mode
WEAPI_AES_KEY    = "0CoJUm6Qyw8W8jud" # cbc
WEAPI_AES_IV     = "0102030405060708" # cbc
LINUXAPI_AES_KEY = "rFgB&h#%2?^eDg:Q" # ecb
EAPI_DIGEST_SALT = "nobody%(url)suse%(text)smd5forencrypt"
EAPI_DATA_SALT   = "%(url)s-36cd479b6b5-%(text)s-36cd479b6b5-%(digest)s"
EAPI_AES_KEY     = "e82ckenh8dichen8" # ecb
# endregion

# region Cryptographic algorithims
def PKCS7_pad(data,bs=AES.BLOCKSIZE):
    return data + (bs - len(data) % bs) * chr(bs - len(data) % bs)

def PKCS7_unpad(data,bs=AES.BLOCKSIZE):
        pad = data[-1]
        if not pad in range(0,bs):
            return data # hack : data isn't padded
        return data[:-pad]

def AESEncrypt(data:str, key:str, iv='',mode=AES.MODE_CBC):    
    cipher = AES(key.encode())        
    if mode == AES.MODE_CBC:
        return cipher.encrypt_cbc_nopadding(PKCS7_pad(data).encode(),iv.encode())
    else:
        return cipher.encrypt_ecb_nopadding(PKCS7_pad(data).encode())

def AESDecrypt(data:str,key:str,iv='',mode=AES.MODE_CBC):       
    cipher = AES(key.encode())
    if type(data) == str : data = data.enc
    if mode == AES.MODE_CBC:
        return PKCS7_unpad(cipher.decrypt_cbc_nopadding(data,iv.encode()))
    else:
        return PKCS7_unpad(cipher.decrypt_ecb_nopadding(data))

def RSAEncrypt(data:str, n , e , reverse=True):
    m = data if not reverse else reversed(data)        
    m, e, N = int(''.join(m).encode('utf-8').hex(), 16), e , n        
    r = pow(m,e,N)
    return HexCompose(hex(r)[2:].zfill(256))
# endregion

# region api-specific crypto routines
def WeapiEncrypt(params, aes_key2=None):
    """Implements /weapi/ Asymmetric encryption"""
    aes_key2 = aes_key2 or RandomString(16)
    params = str(params)
    # 1st go,encrypt the text with aes_key and aes_iv
    params = str(base64.encodebytes(AESEncrypt(
        data=params, key=WEAPI_AES_KEY, iv=WEAPI_AES_IV,mode=AES.MODE_CBC)), encoding='utf-8')
    # 2nd go,encrypt the ENCRYPTED text again,with the 2nd key and aes_iv
    params = str(base64.encodebytes(AESEncrypt(
        data=params, key=aes_key2, iv=WEAPI_AES_IV,mode=AES.MODE_CBC)), encoding='utf-8')
    # 3rd go,generate RSA encrypted encSecKey
    encSecKey = HexDigest(RSAEncrypt(aes_key2, *WEAPI_RSA_PUBKEY))        
    return {
        'params': params,
        'encSecKey': encSecKey
    }

def AbroadDecrypt(result):
    """Decrypts 'abroad:True' messages"""
    return security.c_decrypt_abroad_message(result)

def EapiEncrypt(url,params):
    """Implements EAPI request encryption"""
    url,params = str(url),str(params)
    digest = HashHexDigest(EAPI_DIGEST_SALT % {'url':url,'text':params})
    params = EAPI_DATA_SALT % ({'url':url,'text':params,'digest':digest})
    return {
        'params':HexDigest(AESEncrypt(params,key=EAPI_AES_KEY,mode=AES.MODE_ECB))
    }
    
def EapiDecrypt(cipher):
    """Implements EAPI response decryption"""
    cipher = bytearray(cipher) if isinstance(cipher,str) else cipher
    return AESDecrypt(cipher,EAPI_AES_KEY,mode=AES.MODE_ECB) if cipher else cipher

def LinuxApiEncrypt(params):
    """Implements Linux/Deepin client API encryption"""
    params = str(params)
    return {
        'eparams':HexDigest(AESEncrypt(params,key=LINUXAPI_AES_KEY,mode=AES.MODE_ECB))
    }
# endregion
