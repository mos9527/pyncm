'''# 网易云音乐 APIs'''
import base64
from time import time
from requests.api import head, request
from .. import GetCurrentSession, Session
from .. import logger
from .. import Crypto
import json,zlib,urllib.parse

class LoginRequiredException(Exception):pass
class LoginFailedException(Exception):pass
# region Base models export
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

def _BaseWrapper(requestFunc):
    '''Base wrapper for crypto requests
    '''
    def apiWrapper(apiFunc):
        '''apiFunc -> rtype : (url,plain,[method])'''
        def wrapper(*a,**k):
            ret       = apiFunc(*a,**k)
            url,plain = ret[:2]
            method    = ret[-1] if ret[-1] in ['POST','GET'] else 'POST'        
            rsp = requestFunc(url,plain,method)            
            try:
                return json.loads(rsp.text)
            except json.JSONDecodeError:
                return rsp
        return wrapper
    return apiWrapper

@_BaseWrapper
def WeapiCryptoRequest(url,plain,method):
    '''This apis utilize `/weapi/` calls,seen in web & pc clients'''
    payload = json.dumps({**plain,'csrf_token':GetCurrentSession().csrf_token})
    return GetCurrentSession().request(method,
        GetCurrentSession().HOST + url.replace('/api/','/weapi/'),
        params={'csrf_token':GetCurrentSession().csrf_token},
        data={**Crypto.WeapiCrypto(payload)},
    )
# region Port of `Binaryify/NeteaseCloudMusicApi`
@_BaseWrapper
def LapiCryptoRequest(url,plain,method):
    '''This api proxies over /api/linux/forward,seen in Desktop Linux based clients'''
    payload = {
        'method':method,
        'url':GetCurrentSession().HOST + url,
        'params':plain
    }
    payload = json.dumps(payload)
    return GetCurrentSession().request(method,
        '/api/linux/forward',
        headers={
            **GetCurrentSession().headers, 
            'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
        },
        data={**Crypto.LinuxCrypto(payload)}
    )

@_BaseWrapper
def EapiCryptoRequest(url,plain,method):
    '''This API utilize '/api/' or '/eapi/',seen in mobile clients'''
    cookies = {
        'appver': '6.1.1',
        'buildver':'undefined',   
        'channel':'undefined',
        'deviceId': 'undefined',             
        'mobilename' : 'undefined',        
        'os': 'android',
        'osver':'undefined',            
        'requestId':f'{int(time() * 1000)}_0233',
        'resolution': '1920x1080',        
        'versioncode': '140',
        '__csrf':GetCurrentSession().csrf_token
    }
    payload = {
        **plain,
        'header':cookies
    }
    request = GetCurrentSession().request(method,
        GetCurrentSession().HOST + url,
        headers={
            **GetCurrentSession().headers, 
            'User-Agent':'Mozilla/5.0 (Linux; Android 10; Pixel 2 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Mobile Safari/537.36',
        },
        cookies=cookies,
        data={**Crypto.EapiCrypto(url.replace('/eapi/','/api/'),json.dumps(payload))}
    )
    return request
# endregion
# endregion
from . import miniprograms,album,cloud,cloudsearch,login,playlist,track,user,video