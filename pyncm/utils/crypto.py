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
WEAPI_AES_KEY    = "0CoJUm6Qyw8W8jud" # cbc
WEAPI_AES_IV     = "0102030405060708" # cbc
WEAPI_RSA_PUBKEY = RSAPublicKey(
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7",
    "10001" # textbook rsa without padding
)
WEAPI_RSA_DEFAULT_CRYPTO = (
    'www.mos9527.top!', # maybe spare a little drop-by? ;)
    # plaintext (aes_key_2)
    '8aedbe4ad50512d5ef69e18025ab02b094ef6e96cb352c5dadc69f9a5b9b7a07cdd2b27446bd6273a2cb3ebf8de9cef5564d646cc04718fd6ca99f25dee031a10e93a39ecfa885280d0936d94af034fce82d9cdd285351f5a71f76d9da043a2289a25b588832f0342dec14a41398cdae5dfdda0b6f4f07d72615cbab4d97e395'
    # (key->rsa_pubkey) ciphertext (encSecKey)
)   # signle-block,no padding
LINUXAPI_AES_KEY = "rFgB&h#%2?^eDg:Q" # ecb
EAPI_DIGEST_SALT = "nobody%(url)suse%(text)smd5forencrypt"
EAPI_DATA_SALT   = "%(url)s-36cd479b6b5-%(text)s-36cd479b6b5-%(digest)s"
EAPI_AES_KEY     = "e82ckenh8dichen8" # ecb
CHARSET_BASE62   = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
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
    def RandomString(len, chars=CHARSET_BASE62):
        '''Generates random string of `len` chars within a selected number of chars'''
        return ''.join([random.choice(chars) for i in range(0, len)])
    @staticmethod
    def HexDigest(data : bytearray):
        '''Digests a `bytearray` to a hex string'''
        return ''.join([hex(d)[2:].zfill(2) for d in data])
    @staticmethod
    def HexCompose(hexstr : str):
        '''Composes a hex string back to a `bytearray`'''
        if len(hexstr) % 2:raise Exception('Hex-string length should be an even number')
        return bytearray([int(hexstr[i:i+2],16) for i in range(0,len(hexstr),2)])
    @staticmethod
    def HashDigest(text):
        '''Digests 128 bit md5 hash'''
        HASH = md5(text.encode('utf-8'))
        return HASH.digest()        
    @staticmethod
    def HashHexDigest(text):
        '''Digests 128 bit md5 hash,then digest it as a hexstring'''
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
        n = data
        if reverse:n = reversed(n)
        n, e, N = toInt(''.join(n)), pubkey.e, pubkey.n
        return Crypto.HexCompose(hex(n ** e % N)[2:].zfill(256))
    # endregion
    # endregion
    
    # region Netease crypto
    '''source:https://s3.music.126.net/web/s/core_53f8fab3b18ff334dd7af53eec462c5e.js'''
    @staticmethod
    def WeapiCrypto(params, crypto=WEAPI_RSA_DEFAULT_CRYPTO):
        '''Used in web & PC client'''
        aes_key2,encSecKey = crypto
        params = str(params)
        # 1st go,encrypt the text with aes_key and aes_iv
        params = str(base64.encodebytes(Crypto.AESEncrypt(
            data=params, key=WEAPI_AES_KEY, iv=WEAPI_AES_IV,mode=AES.MODE_CBC)), encoding='utf-8')
        # 2nd go,encrypt the ENCRYPTED text again,with the 2nd key and aes_iv
        params = str(base64.encodebytes(Crypto.AESEncrypt(
            data=params, key=aes_key2, iv=WEAPI_AES_IV,mode=AES.MODE_CBC)), encoding='utf-8')
        # 3rd go,generate RSA encrypted encSecKey
        if not encSecKey:
            # try not to generate this on-the-fly as it's quite slow
            encSecKey = Crypto.HexDigest(Crypto.RSAEncrypt(aes_key2, WEAPI_RSA_PUBKEY))
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
            'eparams':Crypto.HexDigest(Crypto.AESEncrypt(params,key=LINUXAPI_AES_KEY,mode=AES.MODE_ECB))
        }
    
    @staticmethod
    def EapiCrypto(url,params):
        '''Used in mobile and PC clients'''
        url,params = str(url),str(params)
        digest = Crypto.HashHexDigest(EAPI_DIGEST_SALT % {'url':url,'text':params})
        params = EAPI_DATA_SALT % ({'url':url,'text':params,'digest':digest})
        return {
            'params':Crypto.HexDigest(Crypto.AESEncrypt(params,key=EAPI_AES_KEY,mode=AES.MODE_ECB))
        }

    @staticmethod
    def EapiDecrypt(cipher):
        '''Used in mobile clients'''
        cipher = bytearray(cipher) if isinstance(cipher,str) else cipher
        return Crypto.AESDecrypt(cipher,EAPI_AES_KEY,mode=AES.MODE_ECB) if cipher else cipher
    # endregion