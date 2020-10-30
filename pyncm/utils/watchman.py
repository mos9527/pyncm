'''# Watchman.js implementation'''
import json,math,ctypes
from hashlib import md5
from time import time

# region Constant strings
Sc = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
Tc = '='
'''Base64 chars'''
Rb = 'LPc4uQNptC2A6y.R90DOBIroS+qnx/eb3FM8fW1UZG7VmwvksgjhaTKzlXdiYEHJ'
db = 5
'''Default obfuscation chars'''
WM_DID = 'Eyj1ZVEWep5ERQEFFVMuN0xNxLvKykXT' # fallback value
'''DeviceID - XXX - device Id - Probably won't be bothering with this anymore...'''
# endregion
# region Bitwise operations
'''These exsist beacues JS's bit handling is not correct arithmeticly - AND,OR,XOR,NOT,and LS,RS are few examples'''
def _int(v):return ctypes.c_int(v).value
def _lshift(v,bs):
    return _int(v << (bs & 0x1F))
def _rshift(v,bs):
    return _int(v >> (bs & 0x1F))
# Bit shifting only takes care of LS 5 bits
def _logical_rshift(v,bs):
    return _int( ( v % (0xFFFFFFFF + 1)) >> (bs & 0x1F))    
def _truncate(v):
    return v & 0xFFFFFFFF    
# MDN : All javascript bit operations are done on 32 bit integers
def _and(v1,v2): return _int( _truncate(v1) & _truncate(v2))
def  _or(v1,v2): return _int( _truncate(v1) | _truncate(v2))
def _xor(v1,v2): return _int( _truncate(v1) ^ _truncate(v2))
def _not(v1):    return _int(~_truncate(v1))
# endregion
# region MD5
def ha(b, c):
    '''Bitwise sum'''
    d = (b & 65535) + (c & 65535)
    br16 = _rshift(b,16)
    cr16 = _rshift(c,16)
    dr16 = _rshift(d,16)
    r = br16 + cr16 + dr16
    rl16 = _lshift(r,16)    
    return rl16 | d & 65535
def Yb(e):
    '''MD5 hasher'''
    from . import Crypto
    return Crypto.HashDigest(e)
def Zb(e):
    '''MD5 digest hexi-fier'''
    from . import Crypto
    return Crypto.HexDigest(e)
# endregion
# region Special functions
def C(e):
    '''Integer mapping - (-inf,inf) -> [-127,127]'''
    if e < -128:
        return C(128 - (-128 - e))
    if (e >= -128 and e <= 127):
        return e
    if (e > 127):
        return C(-129 + e - 127)
def X(b):
    '''Integer to bytes - int(32 bits) -> [4 bytes]'''
    return [C(b >> 24 & 255),C(b >> 16 & 255),C(b >> 8 & 255),C(b & 255)]
def Z(e):
    '''encodeURIComponent()'''
    return e
def ac(e):
    '''unescape()'''
    return e
def la(e):
    '''parseInt()'''
    return int(e)
def ya(e):    
    '''String to charcode array'''
    return [ord(char) for char in Z(e)] if isinstance(e,str) else e
def Ub(e):
    '''Char to hexdecimal [00,FF] string'''
    c = "0123456789abcdef"
    return c[e >> 4 & 15] + c[e & 15]
def gb(e):
    '''String to hexstring converter'''
    return ''.join([Ub(a) for a in e])
def La(e):    
    '''Simple XOR cipherer'''
    d = [31, 125, -12, 60, 32, 48]
    e = ya(e)
    g = []
    for q in range(0,len(e)):         
        g.append(C(_xor(e[q],d[q % len(d)])))
        g[q] = C(-g[q])
    return gb(g)
def ga(e, c, d, r, g):
    '''Array shuffler'''
    for h in range(0,g):d[r + h] = e[c + h]
def hb(e):
    '''Hexstring to integer array'''
    c = []
    for r in range(0,len(e),2):
        h = _lshift(int(e[r], 16),4)
        m = int(e[r + 1], 16)
        c.append(C(h + m))
    return c    
def Qb(e, c, d=0, r=Rb, g=db):
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
def Sb(e, c=[], d=db):
    '''Characters mapped to another array'''
    r = 3
    h = 0
    g = []
    while (h < len(e)):
        if (h + r <= len(e)):
            g.append(Qb(e, h, r, c, d))
            h += r
        else:
            g.append(Qb(e, h, len(e) - h, c, d));
            break
    return "".join(g)
def Tb(a):
    return Sb(a,Sc,Tc)
def b():
    '''OTP tokenizer'''
    e = int(time() * 1000) # it seems that this timestamp should within 1mo of today's time
    c = math.floor(e / 4294967296)
    d = e % 4294967296
    e = X(c)
    d = X(d)
    c = [ 0 ] * 8    
    ga(e, 0, c, 0, 4);
    ga(d, 0, c, 4, 4);  
    d = [ 0 ] * 8 # should be random nums of [0-255] * 8
    e = [ 0 ] * 16
    for g in range(0,len(c) * 2):
        if (g % 2 == 0):
            f = int(g / 2)
            e[g] = e[g] | (d[f] & 16) >> 4 | (d[f] & 32) >> 3 | (d[f] & 64) >> 2 | (d[f] & 128) >> 1 | (c[f] & 16) >> 3 | (c[f] & 32) >> 2 | (c[f] & 64) >> 1 | (c[f] & 128) >> 0
        else:
            f = math.floor(g / 2)
            e[g] = e[g] | (d[f] & 1) << 0 | (d[f] & 2) << 1 | (d[f] & 4) << 2 | (d[f] & 8) << 3 | (c[f] & 1) << 1 | (c[f] & 2) << 2 | (c[f] & 4) << 3 | (c[f] & 8) << 4
        e[g] = C(e[g])
    c = gb(e)
    c = Zb(Yb(ac(Z(c + "dAWsBhCqtOaNLLJ25hBzWbqWXwiK99Wd"))))
    c = hb(c[:16])
    c = Tb(c+e)
    return c
def bc(c,f=1,g=WM_DID):
    '''Generates hash of our local config'''
    t = ac(Z(str(f) + str(g) + str(c) + "WoeTpXnDDPhiAvsJUUIY3RdAo2PKaVwi"))
    t = Yb(t)
    return La(json.dumps({
        'r': f,      # config.va - should be 1 all the time
        'd': g,      # g || "",device ID
        'b': c,
        't': Tb(t)
    }))
# end region    
def checkToken(deviceId=WM_DID):
    '''Generates `checkToken` parameter
    
    Args:
        deviceId (str, optional): XXX: Device ID fetched. Defaults to WM_DID.

    Returns:
        str
    '''
    return bc(b(),g=deviceId)