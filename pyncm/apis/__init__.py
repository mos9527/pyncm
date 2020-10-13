'''# 网易云音乐 APIs'''
import base64
from logging import getLogger
from time import time
from requests.models import Response
from .. import GetCurrentSession,SetCurrentSession
from .. import logger
from ..utils import Crypto,ncm_client_key
import json,urllib.parse

class LoginRequiredException(Exception):pass
class LoginFailedException(Exception):pass
# region Base models export
LOGIN_REQUIRED = LoginRequiredException('Function needs you to be logged in')

def parse(url):return urllib.parse.urlparse(url)

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

def BaseWrapper(requestFunc):
    '''Base wrapper for crypto requests'''
    def apiWrapper(apiFunc):
        '''apiFunc -> rtype : (url,plain,[method])'''
        def wrapper(*a,**k):
            ret       = apiFunc(*a,**k)
            url,plain = ret[:2]
            method    = ret[-1] if ret[-1] in ['POST','GET'] else 'POST'        
            rsp = requestFunc(url,plain,method)                        
            try:
                return json.loads(rsp.text) if isinstance(rsp,Response) else json.loads(rsp)
            except json.JSONDecodeError:
                return rsp
        return wrapper
    return apiWrapper

def EapiEncipered(func):
    def wrapper(*a,**k):
        payload = func(*a,**k)
        try:            
            return Crypto.EapiDecrypt(payload).decode()
        except:
            return payload
    return wrapper        

@BaseWrapper
def WeapiCryptoRequest(url,plain,method):
    '''This apis utilize `/weapi/` calls,seen in web & pc clients'''
    payload = json.dumps({**plain,'csrf_token':GetCurrentSession().csrf_token})
    return GetCurrentSession().request(method,
        url.replace('/api/','/weapi/'),
        params={'csrf_token':GetCurrentSession().csrf_token},
        data={**Crypto.WeapiCrypto(payload)},
    )
# region Port of `Binaryify/NeteaseCloudMusicApi`
@BaseWrapper
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

@BaseWrapper
@EapiEncipered
def EapiCryptoRequest(url,plain,method):
    '''This API utilize '/api/' or '/eapi/',seen in mobile clients'''
    cookies = {
        'appver': '7.2.24', # the version used for decompilation
        'buildver':'whatever_the_latest_is', # ...these don't matter   
        'channel':'persumably_offical',
        'deviceId': 'pyncm_but_who_cares',   # ...
        'mobilename' : 'Pixel2XL',           # ...as long as these matches our UA
        'os': 'android',
        'osver':'10.0',                      # ...
        'requestId':f'{int(time() * 1000)}_0233',
        'resolution': '2712x1440',
        'versioncode': '240',
        '__csrf':GetCurrentSession().csrf_token,
        **GetCurrentSession().cookies
    }
    payload = {
        **plain,    
        'header':json.dumps(cookies)
    }
    request = GetCurrentSession().request(method,
        url,
        headers={
            **GetCurrentSession().headers, 
            'User-Agent':'NeteaseMusic/7.2.24.1597753235(7002024);Dalvik/2.1.0 (Linux; U; Android 11; Pixel 2 XL Build/RP1A.200720.009)',
            'Referer':None
        },
        cookies=cookies,
        data={**Crypto.EapiCrypto(parse(url).path.replace('/eapi/','/api/'),json.dumps(payload))}
    )
    return request.content
# endregion
# endregion
from . import miniprograms,album,cloud,cloudsearch,login,playlist,track,user,video