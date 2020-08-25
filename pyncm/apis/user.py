'''User related APIs'''
from . import GetCurrentSession,WeapiCryptoRequest,LoginRequiredException

LOGIN_REQUIRED = LoginRequiredException('Function needs you to be logged in')

def LoginRequiredApi(func):
    '''This API needs the user's token'''
    def wrapper(*a,**k):
        if not GetCurrentSession().login_info['success']:raise LOGIN_REQUIRED
        return func(*a,**k)
    return wrapper

def UserIDBasedApi(func):
    '''This API has UID as its first argument'''
    def wrapper(user_id=0,*a,**k):
        if user_id == 0 and GetCurrentSession().login_info['success']:
            user_id = GetCurrentSession().login_info['content']['account']['id']
        elif user_id == 0:
            raise LOGIN_REQUIRED
        return func(user_id,*a,**k)
    return wrapper

@WeapiCryptoRequest
@UserIDBasedApi
def GetUserDetail(user_id = 0):
    '''Retrives one user's detailed infomation

    Args:
        user_id (int): User ID,defaults to 0 (denotes the logged in user)

    Returns:
        dict : The said info
    '''
    return '/weapi/v1/user/detail/%s' % user_id,{}

@WeapiCryptoRequest
@UserIDBasedApi
def GetUserPlaylists(user_id, offset=0, limit=1001):
    '''Fetches a user's playlists

    Args:
        user_id (int): User ID,defaults to 0 (denotes the logged in user)
        offset (int, optional): Where the first comment begins (ordered by time.ascending). Defaults to 0.
        limit (int, optional): How much comment to receive. Defaults to 20.

    Returns:
        dict : The said playlist
    '''    
    return '/weapi/user/playlist',{'offset': str(offset), 'limit': str(limit),'uid': str(user_id)}

SIGNIN_TYPE_MOBILE = 0
SIGNIN_TYPE_WEB    = 1

@WeapiCryptoRequest
@LoginRequiredApi
def Signin(type=0):
    '''Performs `Daily Sigin`

    Args:
        type (int, optional): Const denoted by 'SIGNIN_TYPE_' in this module,Defaults to SIGNIN_TYPE_MOBILE.

    Returns:
        dict : The signin result

    Note:
        SIGNIN_TYPE_MOBILE - 4 EXP
        SIGNIN_TYPE_WEB    - 1 EXP
    '''
    return '/weapi/point/dailyTask',{'type':str(type)}
