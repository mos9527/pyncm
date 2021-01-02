'''# 网易云音乐 APIs

## 编写
对 EAPI (非网页端所用) 请求，抓包后可将数据体 `params=` 后内容丢进 `utils/eapidumper.py` 直接生成相应 Python 函数。
对于 Weapi (网页端，小程序所用) 请求，可在 `core.js` 内下断点后手动编写

编写的所有的 API 过程应遵循下列格式：

@[API 请求类型] # 可根据抓到包的 URL 判断

@[API 限制条件] # 可选

@[API 预、后处理] # 可选

def [API 名] ([API 参数]):

    """[Google 风格多行注释]"""

    return '[API URL]',{[API 参数]}

对于需要 `checkToken` 参数的 API,请使用 `Crypto.checkToken()` 计算 
'''
import base64
from logging import getLogger
from time import time
from requests.models import Response
from .. import GetCurrentSession,SetCurrentSession
from .. import logger
from ..utils import Crypto
import json,urllib.parse

class LoginRequiredException(Exception):pass
class LoginFailedException(Exception):pass
# region Base models export
LOGIN_REQUIRED = LoginRequiredException('Function needs you to be logged in')

def parse(url):return urllib.parse.urlparse(url)

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
                payload = rsp.text if isinstance(rsp,Response) else rsp
                payload = payload.decode() if not isinstance(payload,str) else payload
                return json.loads(payload.strip('\x10')) # weird caveat - they padded plaintext responses as well,though they always end with \x10(16)
            except json.JSONDecodeError:
                return rsp
        return wrapper
    return apiWrapper

def LoginRequiredApi(func):
    '''限制条件 - API 需要事先登录'''
    def wrapper(*a,**k):
        if not GetCurrentSession().login_info['success']:raise LOGIN_REQUIRED
        return func(*a,**k)
    return wrapper

def UserIDBasedApi(func):
    '''限制条件 - API 第一参数为用户 ID，而该参数可留 0 而指代已登录的用户 ID'''
    def wrapper(user_id=0,*a,**k):
        if user_id == 0 and GetCurrentSession().login_info['success']:
            user_id = GetCurrentSession().login_info['content']['account']['id']
        elif user_id == 0:
            raise LOGIN_REQUIRED
        return func(user_id,*a,**k)
    return wrapper

def EapiEncipered(func):
    '''后处理 - 函数值有 Eapi 加密 - 解密并返回原文'''
    def wrapper(*a,**k):
        payload = func(*a,**k)
        try:            
            return Crypto.EapiDecrypt(payload).decode()
        except:
            return payload
    return wrapper        

@BaseWrapper
def WeapiCryptoRequest(url,plain,method):
    '''请求类型 - Weapi - 适用于 网页端、小程序、手机端部分 APIs'''
    payload = json.dumps({**plain,'csrf_token':GetCurrentSession().csrf_token})
    return GetCurrentSession().request(method,
        url.replace('/api/','/weapi/'),
        params={'csrf_token':GetCurrentSession().csrf_token},
        data={**Crypto.WeapiCrypto(payload)},
    )
# region Port of `Binaryify/NeteaseCloudMusicApi`
@BaseWrapper
def LapiCryptoRequest(url,plain,method):
    '''请求类型 - Linux API - 适用于 Linux 客户端部分 APIs'''
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
            'User-Agent':GetCurrentSession().UA_LINUX_API
        },
        data={**Crypto.LinuxCrypto(payload)}
    )

@BaseWrapper
@EapiEncipered
def EapiCryptoRequest(url,plain,method):
    '''请求类型 - Eapi - 适用于 新版客户端绝大部分 APIs'''
    cookies = {
        **GetCurrentSession().CONFIG_EAPI,  
        'requestId':f'{int(time() * 1000)}_0233',      
        '__csrf':GetCurrentSession().csrf_token,
        **GetCurrentSession().cookies,
    }
    payload = {
        **plain,    
        'header':json.dumps(cookies)
    }
    request = GetCurrentSession().request(method,
        url,
        headers={
            **GetCurrentSession().headers, 
            'User-Agent':GetCurrentSession().UA_EAPI,
            'Referer':None
        },
        cookies=cookies,
        data={**Crypto.EapiCrypto(parse(url).path.replace('/eapi/','/api/'),json.dumps(payload))}
    )
    return request.content
# endregion
# endregion
from . import miniprograms,album,cloud,cloudsearch,login,playlist,track,user,video