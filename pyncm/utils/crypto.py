import base64
from Crypto.Cipher import AES
from . import HexCompose,HexDigest,HashHexDigest,RandomString,security

# region secrets
class RSAPublicKey():
    def __init__(self, n, e):
        '''RSA pubkey pubkey & modulus pair,values are interpeted as integers'''
        self.n = int(n, 16)
        self.e = int(e, 16)
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
# endregion

# region dynamic parameters
def GenerateCheckToken():
    '''Generates `checkToken` parameter ,which is needed by a handful of Weapis'''        
    return security.wm_generate_config_chiper_bc(security.wm_generate_OTP_b())
# endregion 

# region base encryption algos
def AESEncrypt(data:str, key:str, mode=AES.MODE_ECB , iv=''):
    '''Basic AES encipher function'''
    def pad(data,blocksize=AES.block_size):return data + (blocksize - len(data) % blocksize) * chr(blocksize - len(data) % blocksize)        
    if mode in [AES.MODE_EAX,AES.MODE_ECB]:
        encryptor = AES.new(key.encode(), mode)
    else:    
        encryptor = AES.new(key.encode(), mode, iv.encode())
    encrypt_aes = encryptor.encrypt(str.encode(pad(data)))
    return encrypt_aes
def AESDecrypt(data:str,key:str,mode=AES.MODE_ECB,iv=''):
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
def RSAEncrypt(data:str, pubkey, reverse=True):
    '''Signle-block textbook RSA encrpytion (c ≡ n ^ e % N),encodes text to hexstring first'''
    n = data if not reverse else reversed(data)        
    n, e, N = int(''.join(n).encode('utf-8').hex(), 16), pubkey.e, pubkey.n
    r = pow(n,e,N)
    return HexCompose(hex(r)[2:].zfill(256))
# endregion

# region api-specific encryption routines
def WeapiEncrypt(params, aes_key2=None):
    '''Used in web & PC client'''
    aes_key2 = aes_key2 or RandomString(16)
    params = str(params)
    # 1st go,encrypt the text with aes_key and aes_iv
    params = str(base64.encodebytes(AESEncrypt(
        data=params, key=WEAPI_AES_KEY, iv=WEAPI_AES_IV,mode=AES.MODE_CBC)), encoding='utf-8')
    # 2nd go,encrypt the ENCRYPTED text again,with the 2nd key and aes_iv
    params = str(base64.encodebytes(AESEncrypt(
        data=params, key=aes_key2, iv=WEAPI_AES_IV,mode=AES.MODE_CBC)), encoding='utf-8')
    # 3rd go,generate RSA encrypted encSecKey
    encSecKey = HexDigest(RSAEncrypt(aes_key2, WEAPI_RSA_PUBKEY))        
    return {
        'params': params,
        'encSecKey': encSecKey
    }
def AbroadDecrypt(result):
    '''Decrypts 'abroad:True' messages.'''
    return security.c_decrypt_abroad_message(result)

'''the following's credit goes to:
    - decompilation of `libpoison.so` : https://juejin.im/post/6844903586879520775
    - Binaryify/NeteaseCloudMusicApi  : https://github.com/Binaryify/NeteaseCloudMusicApi'''
def LinuxApiEncrypt(params):
    '''Used in desktop linux clients'''
    params = str(params)
    # Single-pass AES-128 ECB crypto
    return {
        'eparams':HexDigest(AESEncrypt(params,key=LINUXAPI_AES_KEY,mode=AES.MODE_ECB))
    }
def EapiEncrypt(url,params):
    '''Used in mobile and PC clients'''
    url,params = str(url),str(params)
    digest = HashHexDigest(EAPI_DIGEST_SALT % {'url':url,'text':params})
    params = EAPI_DATA_SALT % ({'url':url,'text':params,'digest':digest})
    return {
        'params':HexDigest(AESEncrypt(params,key=EAPI_AES_KEY,mode=AES.MODE_ECB))
    }
def EapiDecrypt(cipher):
    '''Used in mobile clients'''
    cipher = bytearray(cipher) if isinstance(cipher,str) else cipher
    return AESDecrypt(cipher,EAPI_AES_KEY,mode=AES.MODE_ECB) if cipher else cipher
# endregion
