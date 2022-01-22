# -*- coding: utf-8 -*-
# Miscellaneous implementations of some of  netease's security algorithms
import ctypes,math,json,urllib.parse
from time import time
from . import HashDigest,HexDigest,BASE64

# region secrets
WEAPI_WATCHMAN_PAD = 5
WEAPI_WATCHMAN_SBOX = 'LPc4uQNptC2A6y.R90DOBIroS+qnx/eb3FM8fW1UZG7VmwvksgjhaTKzlXdiYEHJ'
WEAPI_WATCHMAN_KEY = [31, 125, -12, 60, 32, 48]
WEAPI_WATCHMAN_SALT_1 = 'dAWsBhCqtOaNLLJ25hBzWbqWXwiK99Wd'
WEAPI_WATCHMAN_SALT_2 = 'WoeTpXnDDPhiAvsJUUIY3RdAo2PKaVwi'
WEAPI_WATCHMAN_DID = 'Eyj1ZVEWep5ERQEFFVMuN0xNxLvKykXT' 

WEAPI_ABROAD_SBOX = [82, 9, 106, -43, 48, 54, -91, 56, -65, 64, -93, -98, -127, -13, -41, -5, 124, -29, 57, -126, -101, 47, -1, -121, 52, -114, 67, 68, -60, -34, -23, -53, 84, 123, -108, 50, -90, -62, 35, 61, -18, 76, -107, 11, 66, -6, -61, 78, 8, 46, -95, 102, 40, -39, 36, -78, 118, 91, -94, 73, 109, -117, -47, 37, 114, -8, -10, 100, -122, 104, -104, 22, -44, -92, 92, -52, 93, 101, -74, -110, 108, 112, 72, 80, -3, -19, -71, -38, 94, 21, 70, 87, -89, -115, -99, -124, -112, -40, -85, 0, -116, -68, -45, 10, -9, -28, 88, 5, -72, -77, 69, 6, -48, 44, 30, -113, -54, 63, 15, 2, -63, -81, -67, 3, 1, 19, -118, 107, 58, -111, 17, 65, 79, 103, -36, -22, -105, -14, -49, -50, -16, -76, -26, 115, -106, -84, 116, 34, -25, -83, 53, -123, -30, -7, 55, -24, 28, 117, -33, 110, 71, -15, 26, 113, 29, 41, -59, -119, 111, -73, 98, 14, -86, 24, -66, 27, -4, 86, 62, 75, -58, -46, 121, 32, -102, -37, -64, -2, 120, -51, 90, -12, 31, -35, -88, 51, -120, 7, -57, 49, -79, 18, 16, 89, 39, -128, -20, 95, 96, 81, 127, -87, 25, -75, 74, 13, 45, -27, 122, -97, -109, -55, -100, -17, -96, -32, 59, 77, -82, 42, -11, -80, -56, -21, -69, 60, -125, 83, -103, 97, 23, 43, 4, 126, -70, 119, -42, 38, -31, 105, 20, 99, 85, 33, 12, 125]
WEAPI_ABROAD_KEY = 'fuck~#$%^&*(458' # ookay...
WEAPI_ABROAD_IV = ([ord(s) for s in WEAPI_ABROAD_KEY] * 5)[:64]
# `abroad` initalization vector, also acts as its key
# endregion

# region functions to mimic the defficiencies of JS bit operations
def jint(v):return ctypes.c_int(v).value
# Bit shifting only takes care of LS 5 bits
def jls(v,bs):
    return jint(v << (bs & 0x1F))
def jrs(v,bs):
    return jint(v >> (bs & 0x1F))
# some bitwise operations are only done on the least significant 32 bits
def jmask(v):
    return v & 0xFFFFFFFF    
def jxor(v1,v2): return jint( jmask(v1) ^ jmask(v2) )
# endregion

# region common practices
def string_to_charcodes(e):    
    # String to charcode array
    return [ord(char) for char in wm_encode(e)] if isinstance(e,str) else e
def char_to_hex(e):
    # Char to hexdecimal [00,FF] string
    c = "0123456789abcdef"
    return c[e >> 4 & 15] + c[e & 15]
def to_hex_string(e):
    # int array to hex string
    return ''.join([char_to_hex(a) for a in e])
def cast_to_signed(e):
    # casts any integer value to signed char
    if e < -128:
        return cast_to_signed(e + 256)
    if (e >= -128 and e <= 127):
        return e
    if (e > 127):
        return cast_to_signed(e - 256)  
def cast_to_multi_signed(b):
    # casts int32 to multiple signed chars
    return [cast_to_signed(b >> 24 & 255),cast_to_signed(b >> 16 & 255),cast_to_signed(b >> 8 & 255),cast_to_signed(b & 255)]
# endregion 

# region Watchman.js security
def wm_Hash(e):
    # MD5 hasher
    return HashDigest(e)
def wm_HexHash(e):
    # digests md5 hash to hex string
    return HexDigest(e)
def wm_encode(e):
    # encodeURIComponent() in watchman.js. not necessary though.
    return e
def wm_unescape(e):
    # since there's nothing escaped anyway...
    return e
def wm_xor_cipher_La(e):    
    # Simple XOR cipherer
    d = WEAPI_WATCHMAN_KEY
    e = string_to_charcodes(e)
    g = []
    for q in range(0,len(e)):         
        g.append(cast_to_signed(jxor(e[q],d[q % len(d)])))
        g[q] = cast_to_signed(-g[q])
    return to_hex_string(g)
def wm_pbox_ga(e, c, d, r, g):
    # p-box
    for h in range(0,g):d[r + h] = e[c + h]
def wm_hex_to_ints_hb(e):
    # Hexstring to integer array
    c = []
    for r in range(0,len(e),2):
        h = jls(int(e[r], 16),4)
        m = int(e[r + 1], 16)
        c.append(cast_to_signed(h + m))
    return c    
def wm_sbox_Qb(e, c, d=0, r=WEAPI_WATCHMAN_SBOX, g=WEAPI_WATCHMAN_PAD):
    # s-box
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
def wm_apply_sbox_Sb(e, c=[], d=WEAPI_WATCHMAN_PAD):
    # applies sbox to input e
    r = 3
    h = 0
    g = []
    while (h < len(e)):
        if (h + r <= len(e)):
            g.append(wm_sbox_Qb(e, h, r, c, d))
            h += r
        else:
            g.append(wm_sbox_Qb(e, h, len(e) - h, c, d));
            break
    return "".join(g)
def wm_map_string_Tb(a):
    return wm_apply_sbox_Sb(a,BASE64,'=')
def wm_generate_OTP_b():
    # Tokenzies current time
    e = int(time() * 1000) 
    c = math.floor(e / 4294967296)
    d = e % 4294967296
    e = cast_to_multi_signed(c)
    d = cast_to_multi_signed(d)
    c = [ 0 ] * 8    
    wm_pbox_ga(e, 0, c, 0, 4);
    wm_pbox_ga(d, 0, c, 4, 4);  
    d = [ 0 ] * 8 # should be random nums of [0-255] * 8
    e = [ 0 ] * 16
    for g in range(0,len(c) * 2):
        if (g % 2 == 0):
            f = int(g / 2)
            e[g] = e[g] | (d[f] & 16) >> 4 | (d[f] & 32) >> 3 | (d[f] & 64) >> 2 | (d[f] & 128) >> 1 | (c[f] & 16) >> 3 | (c[f] & 32) >> 2 | (c[f] & 64) >> 1 | (c[f] & 128) >> 0
        else:
            f = math.floor(g / 2)
            e[g] = e[g] | (d[f] & 1) << 0 | (d[f] & 2) << 1 | (d[f] & 4) << 2 | (d[f] & 8) << 3 | (c[f] & 1) << 1 | (c[f] & 2) << 2 | (c[f] & 4) << 3 | (c[f] & 8) << 4
        e[g] = cast_to_signed(e[g])
    c = to_hex_string(e)
    c = wm_HexHash(wm_Hash(wm_unescape(wm_encode(c + WEAPI_WATCHMAN_SALT_1))))
    c = wm_hex_to_ints_hb(c[:16])
    c = wm_map_string_Tb(c+e)
    return c
def wm_generate_config_chiper_bc(c,f=1,g=WEAPI_WATCHMAN_DID):
    # Generates checkToken pararmeter with current time-of-day as argument
    t = wm_unescape(wm_encode(str(f) + str(g) + str(c) + WEAPI_WATCHMAN_SALT_2))
    t = wm_Hash(t)
    return wm_xor_cipher_La(json.dumps({
        'r': f,      # config.va - should be 1 all the time
        'd': g,      # g || "",device ID
        'b': c,
        't': wm_map_string_Tb(t)
    }))
# endregion    

# region core.js security
def c_quote_int_as_hex(a):
    return '%' + '%'.join([char_to_hex(i) for i in a])
def c_signed_xor(v1,v2): return jxor(cast_to_signed(v1),cast_to_signed(v2))
def c_apply_sbox(src,map):        
    return [map[(i >> 4 & 15) * 16 + (i & 15)] for i in src]
def c_decrypt_abroad_message(hexstring):
    # Decrypts 'result' parameter when 'abroad' flag is true in responses
    source = wm_hex_to_ints_hb(hexstring)    
    result = []
    boxA = WEAPI_ABROAD_IV
    for i in range(0,len(source),64):
        box = source[i:i+64]
        boxB = c_apply_sbox(c_apply_sbox(box,WEAPI_ABROAD_SBOX),WEAPI_ABROAD_SBOX)
        boxC = [c_signed_xor(boxB[i],boxA[i]) for i in range(0,64)]    
        boxD = [cast_to_signed(boxC[i] + cast_to_signed(-boxA[i])) for i in range(0,64)]    
        boxE = [c_signed_xor(boxD[i],WEAPI_ABROAD_IV[i]) for i in range(0,64)]                
        boxA = source[i:i+64] # S-box operation, getting ready for next one
        result += boxE    
    # last 4 bytes contains length, don't need them for now as we can just strip them away
    result = c_quote_int_as_hex(result[:-4])    
    result = urllib.parse.unquote(result).strip('\x00')  
    return result
# endregion