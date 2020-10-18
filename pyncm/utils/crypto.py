'''Implementation of some of NE's crypto functions'''
import base64
from Crypto.Cipher import AES
from Crypto.Random import random
from hashlib import md5
from . import checkToken
class RSAPublicKey():
    '''
        RSA Publickey object,where

            n   :   modulus
            e   :   exponet
        All values are stored as integers
    '''
    def __init__(self, n, e):
        self.n = int(n, 16)
        self.e = int(e, 16)

# region Constant values
weapi_aes_key    = "0CoJUm6Qyw8W8jud" # cbc
weapi_aes_iv     = "0102030405060708" # cbc
weapi_rsa_pubkey = RSAPublicKey(
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7",
    "10001" # signle-block,no padding
)
weapi_rsa_default_crypto = (
    'mos9527ItoooItop', 
    # plaintext (aes_key_2)
    '01a1c399271006da676da55763419f10f0e589515c49530b33418eec82202fc42dae0cd3aa4a2b7bdc3dafa7c6a918e405f3cdbc5d0349ef86913fc2dbe8764ed782e202e7828b547e85f6ae28b8b120bcf5fd3777a55731521612dcaff9813246a42876303b0f2307c9f264671ddc87159ff162e689fdfae5acb3af10250754'
    # (key->rsa_pubkey) ciphertext (encSecKey)
)   # signle-block,no padding
linuxapi_aes_key = "rFgB&h#%2?^eDg:Q" # ecb
eapi_digest_salt = "nobody%(url)suse%(text)smd5forencrypt"
eapi_data_salt   = "%(url)s-36cd479b6b5-%(text)s-36cd479b6b5-%(digest)s"
eapi_aes_key     = "e82ckenh8dichen8" # ecb
randstr_charset  = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
# endregion

def PadWithRemainder(data,blocksize=AES.block_size):
    '''Pads with the remaing length of byte thats needs until our length is a intergal multipule of blocksize'''
    return data + (blocksize - len(data) % blocksize) * chr(blocksize - len(data) % blocksize)

def UnpadRemainder(data):
    '''The reverse funtion of `PadWithRemainder`'''
    pad = data[-1]
    if not pad in range(0,AES.block_size):return data # data isn't padded
    return data[:-pad]

class Crypto():
    '''The cryptography toolkit'''
    # region Base cryptograhpy methods
    # region Utility
    checkToken = checkToken
    @staticmethod
    def RandomString(len, chars=randstr_charset):
        '''Generates random string of `len` chars within a selected number of chars'''
        return ''.join([random.choice(chars) for i in range(0, len)])
    @staticmethod
    def HexDigest(data : bytearray):
        '''Digests a `bytearray` to a hex string'''
        return ''.join([hex(d)[2:].zfill(2) for d in data])
    @staticmethod
    def HexCompose(hexstr : str):
        '''Composes a hex string back to a `bytearray`'''
        if len(hexstr) % 2:raise Exception('Hex-string length should be a even number')
        return bytearray([int(hexstr[i:i+2],16) for i in range(0,len(hexstr),2)])
    @staticmethod
    def HashDigest(text):
        '''Hexdecimal MD5 hash generator'''
        HASH = md5(text.encode('utf-8'))
        return HASH.digest()        
    @staticmethod
    def HashHexDigest(text):
        '''Hexdecimal MD5 hash generator'''
        return Crypto.HexDigest( Crypto.HashDigest(text) )
    # endregion
    # region Cryptos
    @staticmethod
    def AESEncrypt(
        data:str, key:str, mode=AES.MODE_ECB , iv='',padder=PadWithRemainder        
    ):
        '''Basic AES encipher function'''
        if mode in [AES.MODE_EAX,AES.MODE_ECB]:
            encryptor = AES.new(key.encode(), mode)
        else:    
            encryptor = AES.new(key.encode(), mode, iv.encode())
        encrypt_aes = encryptor.encrypt(str.encode(padder(data)))
        return encrypt_aes

    @staticmethod
    def AESDecrypt(
        data:str,key:str,mode=AES.MODE_ECB,iv='',unpadder=UnpadRemainder
    ):
        '''Basic AES decipher funtion'''
        if mode in [AES.MODE_EAX,AES.MODE_ECB]:
            decryptor = AES.new(key.encode(), mode)
        else:    
            decryptor = AES.new(key.encode(), mode, iv.encode())
        decrypted_aes = decryptor.decrypt(data)
        return unpadder(decrypted_aes)

    @staticmethod
    def RSAEncrypt(data:str, pubkey: RSAPublicKey, reverse=True):
        '''Signle-block textbook RSA encrpytion (c ≡ n ^ e % N),encodes text to hexstring first'''
        def toInt(s): return int(s.encode('utf-8').hex(), 16)
        n = data # do not modify in place
        if reverse:n = reversed(n)
        n, e, N = toInt(''.join(n)), pubkey.e, pubkey.n
        return Crypto.HexCompose(hex(n ** e % N)[2:].zfill(256))
    # endregion
    # endregion
    
    # region Netease crypto
    '''source:https://s3.music.126.net/web/s/core_53f8fab3b18ff334dd7af53eec462c5e.js'''
    @staticmethod
    def WeapiCrypto(params, crypto=weapi_rsa_default_crypto):
        '''Used in web & PC client'''
        aes_key2,encSecKey = crypto
        params = str(params)
        # 1st go,encrypt the text with aes_key and aes_iv
        params = str(base64.encodebytes(Crypto.AESEncrypt(
            data=params, key=weapi_aes_key, iv=weapi_aes_iv,mode=AES.MODE_CBC)), encoding='utf-8')
        # 2nd go,encrypt the ENCRYPTED text again,with the 2nd key and aes_iv
        params = str(base64.encodebytes(Crypto.AESEncrypt(
            data=params, key=aes_key2, iv=weapi_aes_iv,mode=AES.MODE_CBC)), encoding='utf-8')
        # 3rd go,generate RSA encrypted encSecKey
        if not encSecKey:
            # try not to generate this on-the-fly as it's quite slow
            encSecKey = Crypto.HexDigest(Crypto.RSAEncrypt(aes_key2, weapi_rsa_pubkey))
        return {
            'params': params,
            'encSecKey': encSecKey
        }

    '''source:
        - decompilation of `libpoison.so` : https://juejin.im/user/2383396938455821
        - Binaryify/NeteaseCloudMusicApi  : https://github.com/Binaryify/NeteaseCloudMusicApi/blob/master/util/crypto.js'''
    @staticmethod
    def LinuxCrypto(params):
        '''Used in desktop linux clients'''
        params = str(params)
        # Single-pass AES-128 ECB crypto
        return {
            'eparams':Crypto.HexDigest(Crypto.AESEncrypt(params,key=linuxapi_aes_key,mode=AES.MODE_ECB))
        }
    
    @staticmethod
    def EapiCrypto(url,params):
        '''Used in mobile clients'''
        url,params = str(url),str(params)
        digest = Crypto.HashHexDigest(eapi_digest_salt % {'url':url,'text':params})
        params = eapi_data_salt % ({'url':url,'text':params,'digest':digest})
        return {
            'params':Crypto.HexDigest(Crypto.AESEncrypt(params,key=eapi_aes_key,mode=AES.MODE_ECB))
        }

    @staticmethod
    def EapiDecrypt(cipher):
        '''Used in mobile clients'''
        cipher = bytearray(cipher) if isinstance(cipher,str) else cipher
        return Crypto.AESDecrypt(cipher,eapi_aes_key,mode=AES.MODE_ECB) if cipher else cipher
    # endregion