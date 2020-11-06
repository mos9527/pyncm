'''用户 - User 有关 APIs'''
from . import WeapiCryptoRequest,UserIDBasedApi,LoginRequiredApi

@WeapiCryptoRequest
@UserIDBasedApi
def GetUserDetail(user_id = 0):
    '''网页端 - 获取某用户资料详情

    Args:
        user_id (int): 用户 ID。置 0 表示当前已登录的用户 . defaults to 0

    Returns:
        dict
    '''
    return '/weapi/v1/user/detail/%s' % user_id,{}

@WeapiCryptoRequest
@UserIDBasedApi
def GetUserPlaylists(user_id, offset=0, limit=1001):
    '''网页端 - 获取某用户创建的歌单

    Args:
        user_id (int): 用户 ID。置 0 表示当前已登录的用户 . defaults to 0
        offset (int, optional): 获取偏移数. Defaults to 0.
        limit (int, optional): 单次获取量. Defaults to 30.

    Returns:
        dict
    '''    
    return '/weapi/user/playlist',{'offset': str(offset), 'limit': str(limit),'uid': str(user_id)}

@WeapiCryptoRequest
@LoginRequiredApi
def GetUserArtistSubs(limit=30):
    '''网页端 - 获取收藏歌手内容
    Args:
        limit (int, optional): 单次获取量. Defaults to 30.

    Returns:
        dict
    '''
    return '/api/artist/sublist', {"limit": str(limit)}

SIGNIN_TYPE_MOBILE = 0
'''移动端签到 +4 EXP'''
SIGNIN_TYPE_WEB    = 1
'''网页端签到 +1 EXP'''

@WeapiCryptoRequest
@LoginRequiredApi
def SetSignin(type=0):
    '''移动端、PC端 - 每日签到

    Args:
        type (int, optional): 签到类型，请使用本模块内 SIGNIN_TYPE_... 之一 .Defaults to SIGNIN_TYPE_MOBILE.

    Returns:
        dict
    '''
    return '/weapi/point/dailyTask',{'type':str(type)}
