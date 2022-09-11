# -*- coding: utf-8 -*-
"""Miscellaneous implementations of some of netease's security algorithms
Implemented:
- `abroad` parameter decryption
"""
import ctypes,urllib.parse
from hashlib import md5
from base64 import b64encode
# region secrets
WEAPI_ABROAD_SBOX = (
    82   ,9    ,106  ,-43  ,48   ,54   ,-91  ,56   ,
    -65  ,64   ,-93  ,-98  ,-127 ,-13  ,-41  ,-5   ,
    124  ,-29  ,57   ,-126 ,-101 ,47   ,-1   ,-121 ,
    52   ,-114 ,67   ,68   ,-60  ,-34  ,-23  ,-53  ,
    84   ,123  ,-108 ,50   ,-90  ,-62  ,35   ,61   ,
    -18  ,76   ,-107 ,11   ,66   ,-6   ,-61  ,78   ,
    8    ,46   ,-95  ,102  ,40   ,-39  ,36   ,-78  ,
    118  ,91   ,-94  ,73   ,109  ,-117 ,-47  ,37   ,
    114  ,-8   ,-10  ,100  ,-122 ,104  ,-104 ,22   ,
    -44  ,-92  ,92   ,-52  ,93   ,101  ,-74  ,-110 ,
    108  ,112  ,72   ,80   ,-3   ,-19  ,-71  ,-38  ,
    94   ,21   ,70   ,87   ,-89  ,-115 ,-99  ,-124 ,
    -112 ,-40  ,-85  ,0    ,-116 ,-68  ,-45  ,10   ,
    -9   ,-28  ,88   ,5    ,-72  ,-77  ,69   ,6    ,
    -48  ,44   ,30   ,-113 ,-54  ,63   ,15   ,2    ,
    -63  ,-81  ,-67  ,3    ,1    ,19   ,-118 ,107  ,
    58   ,-111 ,17   ,65   ,79   ,103  ,-36  ,-22  ,
    -105 ,-14  ,-49  ,-50  ,-16  ,-76  ,-26  ,115  ,
    -106 ,-84  ,116  ,34   ,-25  ,-83  ,53   ,-123 ,
    -30  ,-7   ,55   ,-24  ,28   ,117  ,-33  ,110  ,
    71   ,-15  ,26   ,113  ,29   ,41   ,-59  ,-119 ,
    111  ,-73  ,98   ,14   ,-86  ,24   ,-66  ,27   ,
    -4   ,86   ,62   ,75   ,-58  ,-46  ,121  ,32   ,
    -102 ,-37  ,-64  ,-2   ,120  ,-51  ,90   ,-12  ,
    31   ,-35  ,-88  ,51   ,-120 ,7    ,-57  ,49   ,
    -79  ,18   ,16   ,89   ,39   ,-128 ,-20  ,95   ,
    96   ,81   ,127  ,-87  ,25   ,-75  ,74   ,13   ,
    45   ,-27  ,122  ,-97  ,-109 ,-55  ,-100 ,-17  ,
    -96  ,-32  ,59   ,77   ,-82  ,42   ,-11  ,-80  ,
    -56  ,-21  ,-69  ,60   ,-125 ,83   ,-103 ,97   ,
    23   ,43   ,4    ,126  ,-70  ,119  ,-42  ,38   ,
    -31  ,105  ,20   ,99   ,85   ,33   ,12   ,125
)
WEAPI_ABROAD_KEY = 'fuck~#$%^&*(458' # ookay...,
WEAPI_ABROAD_IV = ([ord(s) for s in WEAPI_ABROAD_KEY] * 5)[:64]
# 'abroad' parameter key & CBC IV
ID_XOR_KEY_1 = b'3go8&$8*3*3h0k(2)2'
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
    return [ord(char) for char in e] if isinstance(e,str) else e
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
def wm_hex_to_ints_hb(e):
    # Hexstring to integer array
    c = []
    for r in range(0,len(e),2):
        h = jls(int(e[r], 16),4)
        m = int(e[r + 1], 16)
        c.append(cast_to_signed(h + m))
    return c
# endregion 

# region core.js security
def c_quote_int_as_hex(a):
    return '%' + '%'.join([char_to_hex(i) for i in a])
def c_signed_xor(v1,v2): 
    return jxor(cast_to_signed(v1),cast_to_signed(v2))
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
        boxA = source[i:i+64]
        result += boxE    
    # last 4 bytes contains length, don't need them for now as we can just strip them away
    result = c_quote_int_as_hex(result[:-4])    
    result = urllib.parse.unquote(result).strip('\x00')  
    return result
# endregion

# region cloudmusic.dll (Windows) security
def cloudmusic_dll_encode_id(some_id):
    # XORs bytes then returns its base64 MD5 hash. Used in encodeAnonymousId
    # Searching for ID_XOR_KEY_1 in cloudmusic.dll will get you to their implementation
    xored = bytearray([c ^ ID_XOR_KEY_1[idx % len(ID_XOR_KEY_1)] for idx, c in enumerate(some_id.encode())])
    digest = md5(xored).digest()
    return b64encode(digest).decode()
# endregion