'''Implementation of some of NE's crypto functions'''
import base64,json,math,ctypes
from Crypto.Cipher import AES
from Crypto.Random import random
from hashlib import md5
from hashlib import md5
from time import time

class RSAPublicKey():
    def __init__(self, n, e):
        '''RSA pubkey pubkey & modulus pair,values are interpeted as integers'''
        self.n = int(n, 16)
        self.e = int(e, 16)
# region Constant values
WEAPI_AES_KEY    = "0CoJUm6Qyw8W8jud" # cbc
WEAPI_AES_IV     = "0102030405060708" # cbc
WEAPI_RSA_PUBKEY = RSAPublicKey(
    "00e0b509f6259df8642dbc35662901477df22677ec152b5ff68ace615bb7b725152b3ab17a876aea8a5aa76d2e417629ec4ee341f56135fccf695280104e0312ecbda92557c93870114af6c9d05c4f7f0c3685b7a46bee255932575cce10b424d813cfe4875d3e82047b97ddef52741d546b8e289dc6935b3ece0462db0a22b8e7",
    "10001" # textbook rsa without padding
)
LINUXAPI_AES_KEY = "rFgB&h#%2?^eDg:Q" # ecb
EAPI_DIGEST_SALT = "nobody%(url)suse%(text)smd5forencrypt"
EAPI_DATA_SALT   = "%(url)s-36cd479b6b5-%(text)s-36cd479b6b5-%(digest)s"
EAPI_AES_KEY     = "e82ckenh8dichen8" # ecb

BASE62           = 'PJArHa0dpwhvMNYqKnTbitWfEmosQ9527ZBx46IXUgOzD81VuSFyckLRljG3eC'
BASE64 = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'

_obfs_Rb = 'LPc4uQNptC2A6y.R90DOBIroS+qnx/eb3FM8fW1UZG7VmwvksgjhaTKzlXdiYEHJ'
_obfs_db = 5

WM_DID = 'Eyj1ZVEWep5ERQEFFVMuN0xNxLvKykXT' 
'''DeviceID - for checkToken (watchman.js)'''
# endregion

# region checkToken (watchman.js) stuff
# region Bitwise operations
def _int(v):return ctypes.c_int(v).value
def _lshift(v,bs):
    return _int(v << (bs & 0x1F))
def _rshift(v,bs):
    return _int(v >> (bs & 0x1F))
# Bit shifting only takes care of LS 5 bits
def _truncate(v):
    return v & 0xFFFFFFFF    
# MDN : All javascript bit operations are done on 32 bit integers
def _xor(v1,v2): return _int( _truncate(v1) ^ _truncate(v2))
# endregion
# region MD5
def _hash_Yb(e):
    '''MD5 hasher'''
    from . import Crypto
    return Crypto.HashDigest(e)
def _hex_Zb(e):
    '''MD5 digest hexi-fier'''
    from . import Crypto
    return Crypto.HexDigest(e)
# endregion
# region Special functions
def _map_int_C(e):
    '''Integer mapping - (-inf,inf) -> [-127,127]'''
    if e < -128:
        return _map_int_C(128 - (-128 - e))
    if (e >= -128 and e <= 127):
        return e
    if (e > 127):
        return _map_int_C(-129 + e - 127)
def _to_bytes_X(b):
    '''Integer to bytes - int(32 bits) -> [4 bytes]'''
    return [_map_int_C(b >> 24 & 255),_map_int_C(b >> 16 & 255),_map_int_C(b >> 8 & 255),_map_int_C(b & 255)]
def _encodeURIComponent_Z(e):
    '''encodeURIComponent()'''
    return e
def _unescape_ac(e):
    '''unescape()'''
    return e
def _charcodes_ya(e):    
    '''String to charcode array'''
    return [ord(char) for char in _encodeURIComponent_Z(e)] if isinstance(e,str) else e
def _to_hex_Ub(e):
    '''Char to hexdecimal [00,FF] string'''
    c = "0123456789abcdef"
    return c[e >> 4 & 15] + c[e & 15]
def _str_to_hex_gb(e):
    '''String to hexstring converter'''
    return ''.join([_to_hex_Ub(a) for a in e])
def _xor_with_array_La(e):    
    '''Simple XOR cipherer'''
    d = [31, 125, -12, 60, 32, 48]
    e = _charcodes_ya(e)
    g = []
    for q in range(0,len(e)):         
        g.append(_map_int_C(_xor(e[q],d[q % len(d)])))
        g[q] = _map_int_C(-g[q])
    return _str_to_hex_gb(g)
def _shuffle_ga(e, c, d, r, g):
    '''Array shuffler'''
    for h in range(0,g):d[r + h] = e[c + h]
def _hexstr_to_int_hb(e):
    '''Hexstring to integer array'''
    c = []
    for r in range(0,len(e),2):
        h = _lshift(int(e[r], 16),4)
        m = int(e[r + 1], 16)
        c.append(_map_int_C(h + m))
    return c    
def _obfuscate_array_Qb(e, c, d=0, r=_obfs_Rb, g=_obfs_db):
    '''Integer array to obfuscated string'''
    h, m,g = 0,[],str(g)
    def push(*a):m.extend(a)
    if d == 1:
        d = e[c];
        h = 0;
        push(r[ d >> 2 & 63], r[(d << 4 & 48) + (h >> 4 & 15)], g, g)
    elif d == 2:
        d = e[c];
        h = e[c + 1];
        e = 0;
        push(r[d >> 2 & 63], r[(d << 4 & 48) + (h >> 4 & 15)], r[(h << 2 & 60) + (e >> 6 & 3)], g)
    elif d == 3:
        d = e[c];
        h = e[c + 1];
        e = e[c + 2];
        push(r[d >> 2 & 63], r[(d << 4 & 48) + (h >> 4 & 15)], r[(h << 2 & 60) + (e >> 6 & 3)], r[e & 63])
    else:
        return None
    return ''.join(m)
def _double_mapping_Sb(e, c=[], d=_obfs_db):
    '''Characters mapped to another array'''
    r = 3
    h = 0
    g = []
    while (h < len(e)):
        if (h + r <= len(e)):
            g.append(_obfuscate_array_Qb(e, h, r, c, d))
            h += r
        else:
            g.append(_obfuscate_array_Qb(e, h, len(e) - h, c, d));
            break
    return "".join(g)
def _map_string_Tb(a):
    return _double_mapping_Sb(a,BASE64,'=')
def _generate_OTP_b():
    '''OTP tokenizer'''
    e = int(time() * 1000) # it seems that this timestamp should within 1mo of today's time
    c = math.floor(e / 4294967296)
    d = e % 4294967296
    e = _to_bytes_X(c)
    d = _to_bytes_X(d)
    c = [ 0 ] * 8    
    _shuffle_ga(e, 0, c, 0, 4);
    _shuffle_ga(d, 0, c, 4, 4);  
    d = [ 0 ] * 8 # should be random nums of [0-255] * 8
    e = [ 0 ] * 16
    for g in range(0,len(c) * 2):
        if (g % 2 == 0):
            f = int(g / 2)
            e[g] = e[g] | (d[f] & 16) >> 4 | (d[f] & 32) >> 3 | (d[f] & 64) >> 2 | (d[f] & 128) >> 1 | (c[f] & 16) >> 3 | (c[f] & 32) >> 2 | (c[f] & 64) >> 1 | (c[f] & 128) >> 0
        else:
            f = math.floor(g / 2)
            e[g] = e[g] | (d[f] & 1) << 0 | (d[f] & 2) << 1 | (d[f] & 4) << 2 | (d[f] & 8) << 3 | (c[f] & 1) << 1 | (c[f] & 2) << 2 | (c[f] & 4) << 3 | (c[f] & 8) << 4
        e[g] = _map_int_C(e[g])
    c = _str_to_hex_gb(e)
    c = _hex_Zb(_hash_Yb(_unescape_ac(_encodeURIComponent_Z(c + "dAWsBhCqtOaNLLJ25hBzWbqWXwiK99Wd"))))
    c = _hexstr_to_int_hb(c[:16])
    c = _map_string_Tb(c+e)
    return c
def _generate_config_chiper_bc(c,f=1,g=WM_DID):
    '''Generates cipher of our local config'''
    t = _unescape_ac(_encodeURIComponent_Z(str(f) + str(g) + str(c) + "WoeTpXnDDPhiAvsJUUIY3RdAo2PKaVwi"))
    t = _hash_Yb(t)
    return _xor_with_array_La(json.dumps({
        'r': f,      # config.va - should be 1 all the time
        'd': g,      # g || "",device ID
        'b': c,
        't': _map_string_Tb(t)
    }))
# endregion    
# endregion    

class Crypto():
    '''The cryptography ...things'''
    # region Base cryptograhpy methods
    # region Utility
    @staticmethod
    def RandomString(len, chars=BASE62):
        '''Generates random string of `len` chars within a selected number of chars'''
        return ''.join([random.choice(chars) for i in range(0, len)])
    @staticmethod
    def HexDigest(data : bytearray):
        '''Digests a `bytearray` to a hex string'''
        return ''.join([hex(d)[2:].zfill(2) for d in data])
    @staticmethod
    def HexCompose(hexstr : str):
        '''Composes a hex string back to a `bytearray`'''
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
    def checkToken(deviceId=WM_DID):
        '''Generates `checkToken` parameter
        
        Args:
            deviceId (str, optional): XXX: Device ID fetched. Defaults to WM_DID.

        Returns:
            str
        '''
        return _generate_config_chiper_bc(_generate_OTP_b(),g=deviceId)
    @staticmethod
    def AESEncrypt(
        data:str, key:str, mode=AES.MODE_ECB , iv=''       
    ):
        '''Basic AES encipher function'''
        def pad(data,blocksize=AES.block_size):return data + (blocksize - len(data) % blocksize) * chr(blocksize - len(data) % blocksize)        
        if mode in [AES.MODE_EAX,AES.MODE_ECB]:
            encryptor = AES.new(key.encode(), mode)
        else:    
            encryptor = AES.new(key.encode(), mode, iv.encode())
        encrypt_aes = encryptor.encrypt(str.encode(pad(data)))
        return encrypt_aes
    @staticmethod
    def AESDecrypt(
        data:str,key:str,mode=AES.MODE_ECB,iv=''
    ):
        '''Basic AES decipher funtion'''
        def unpad(data):
            pad = data[-1]
            if not pad in range(0,AES.block_size):return data # data isn't padded
            return data[:-pad]
        if mode in [AES.MODE_EAX,AES.MODE_ECB]:
            decryptor = AES.new(key.encode(), mode)
        else:    
            decryptor = AES.new(key.encode(), mode, iv.encode())
        decrypted_aes = decryptor.decrypt(data)
        return unpad(decrypted_aes)
    @staticmethod
    def RSAEncrypt(data:str, pubkey: RSAPublicKey, reverse=True):
        '''Signle-block textbook RSA encrpytion (c ≡ n ^ e % N),encodes text to hexstring first'''
        n = data if not reverse else reversed(data)        
        n, e, N = int(''.join(n).encode('utf-8').hex(), 16), pubkey.e, pubkey.n
        r = pow(n,e,N) # n ** e % N - modular exponetiation
        return Crypto.HexCompose(hex(r)[2:].zfill(256))
    # endregion
    # endregion
    # region Netease crypto
    '''source:core.js thingy'''
    @staticmethod
    def WeapiCrypto(params, aes_key2=None):
        '''Used in web & PC client'''
        aes_key2 = aes_key2 or Crypto.RandomString(16)
        params = str(params)
        # 1st go,encrypt the text with aes_key and aes_iv
        params = str(base64.encodebytes(Crypto.AESEncrypt(
            data=params, key=WEAPI_AES_KEY, iv=WEAPI_AES_IV,mode=AES.MODE_CBC)), encoding='utf-8')
        # 2nd go,encrypt the ENCRYPTED text again,with the 2nd key and aes_iv
        params = str(base64.encodebytes(Crypto.AESEncrypt(
            data=params, key=aes_key2, iv=WEAPI_AES_IV,mode=AES.MODE_CBC)), encoding='utf-8')
        # 3rd go,generate RSA encrypted encSecKey
        encSecKey = Crypto.HexDigest(Crypto.RSAEncrypt(aes_key2, WEAPI_RSA_PUBKEY))        
        return {
            'params': params,
            'encSecKey': encSecKey
        }
    '''source:
        - decompilation of `libpoison.so` : https://juejin.im/post/6844903586879520775
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