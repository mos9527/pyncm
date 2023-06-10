# -*- coding: utf-8 -*-
"""PyNCM 网易云音乐 API 封装

本模块提供各种网易云音乐 API 的 Python 封装，及编写新 API 所需的加密修饰器

模块使用可参考子模块说明，如::

    ...
    def GetTrackAudio(song_ids: list, bitrate=320000, encodeType="aac"):
        PC 端 - 获取歌曲音频详情（文件URL、MD5...）

        Args:
            song_ids (list): 歌曲 ID
            bitrate (int, optional): 比特率 (96k SQ 320k HQ 320k+ Lossless/SQ). Defaults to 320000
            encodeType (str, optional) Defaults to `aac`
    ...

使用 `pyncm.apis.GetTrackAudio` 即可

编写新 API
- EAPI
    在获得相关 API 路径和参数后(可参考 [Binaryify 大佬的视频 ](https://www.bilibili.com/video/BV1PY41147r9))

    可参考已有 API 函数格式编写相关 PyNCM API. 各API模式修饰器已在本文件注释
- WEAPI
    由于Weapi使用不对称加密，截取Weapi可从浏览器内断点尝试

    一般在 `encSecKey` 处下断点即可，具体方法不再阐述
"""

from random import randrange
from functools import wraps
from httpx import Response
from ..utils.crypto import (
    EapiDecrypt,
    EapiEncrypt,
    LinuxApiEncrypt,
    WeapiEncrypt,
    AbroadDecrypt,
)
from .. import GetCurrentSession, logger
import json, urllib.parse

class LoginRequiredException(Exception):
    pass

class LoginFailedException(Exception):
    pass

LOGIN_REQUIRED = LoginRequiredException("需要登录")

def _BaseWrapper(requestFunc):
    """API加密函数通用修饰器
    
    实际使用请参考以下其他 Wrapper::
        
        LoginRequiredApi
        UserIDBasedApi
        WeapiCryptoRequest
        LapiCryptoRequest
        EapiCryptoRequest
    """
    @wraps(requestFunc)
    def apiWrapper(apiFunc):
        @wraps(apiFunc)
        async def wrapper(*a, **k):
            ret = apiFunc(*a, **k)
            url, payload = ret[:2]
            method = ret[-1] if ret[-1] in ["POST", "GET"] else "POST"            
            logger.debug('TYPE=%s API=%s.%s %s url=%s deviceId=%s payload=%s' % (
                requestFunc.__name__.split('Crypto')[0].upper(),
                apiFunc.__module__,
                apiFunc,
                method,
                url,
                GetCurrentSession().deviceId,
                payload)
            )
            rsp = await requestFunc(url, payload, method)
            try:
                payload = rsp.text if isinstance(rsp, Response) else rsp
                payload = payload.decode() if not isinstance(payload, str) else payload
                payload = json.loads(payload.strip("\x10"))
                if "abroad" in payload and payload["abroad"]: 
                    # Addresses Issue #15
                    # This however, has some unforeseen side-effects. Mainly due to its diffrences
                    # with non-abraod responses.                    
                    logger.warn('Detected "abroad" payload. API response might differ in format!')
                    real_payload = AbroadDecrypt(payload["result"])
                    payload = {"result":json.loads(real_payload)}
                    # We'll let the user know about it
                    payload['abroad'] = True
                return payload
            except json.JSONDecodeError as e:
                logger.error('Response is not valid JSON : %s' % e)
                logger.error('Response : %s',rsp)
                return rsp

        return wrapper

    return apiWrapper


def LoginRequiredApi(func):
    """API 需要事先登录"""
    @wraps(func)
    def wrapper(*a, **k):
        if not GetCurrentSession().login_info["success"]:
            raise LOGIN_REQUIRED
        return func(*a, **k)

    return wrapper


def UserIDBasedApi(func):
    """API 第一参数为用户 ID，而该参数可留 0 而指代已登录的用户 ID"""
    @wraps(func)
    def wrapper(user_id=0, *a, **k):
        if user_id == 0 and GetCurrentSession().login_info["success"]:
            user_id = GetCurrentSession().uid
        elif user_id == 0:
            raise LOGIN_REQUIRED
        return func(user_id, *a, **k)

    return wrapper

@_BaseWrapper
async def WeapiCryptoRequest(url, plain, method):
    """Weapi - 适用于 网页端、小程序、手机端部分 APIs"""    
    sess = GetCurrentSession()
    payload = json.dumps({**plain, "csrf_token": sess.csrf_token})
    return await sess.request(
        method,
        url.replace("/api/", "/weapi/"),
        params={"csrf_token": sess.csrf_token},
        data={**WeapiEncrypt(payload)},
    )
    
# 来自 https://github.com/Binaryify/NeteaseCloudMusicApi
@_BaseWrapper
async def LapiCryptoRequest(url, plain, method):
    """Linux API - 适用于Linux客户端部分APIs"""
    payload = {"method": method, "url": GetCurrentSession().HOST + url, "params": plain}
    payload = json.dumps(payload)
    return await GetCurrentSession().request(
        method,
        "/api/linux/forward",
        headers={"User-Agent": GetCurrentSession().UA_LINUX_API},
        data={**LinuxApiEncrypt(payload)},
    )

# 来自 https://github.com/Binaryify/NeteaseCloudMusicApi
@_BaseWrapper
async def EapiCryptoRequest(url, plain, method):
    """Eapi - 适用于新版客户端绝大部分API"""    
    payload = {**plain, "header": json.dumps({
        **GetCurrentSession().eapi_config,
        "requestId": str(randrange(20000000,30000000))
    })}
    digest = EapiEncrypt(urllib.parse.urlparse(url).path.replace("/eapi/", "/api/"), json.dumps(payload))    
    request = await GetCurrentSession().request(
        method,
        url,
        headers={"User-Agent": GetCurrentSession().UA_EAPI, "Referer": ''},
        cookies={
            **GetCurrentSession().eapi_config
        },
        data={
            **digest
        },
    )
    payload = request.content
    try:
        return EapiDecrypt(payload).decode()
    except:
        return payload


from . import (
    artist,
    miniprograms,
    album,
    cloud,
    cloudsearch,
    login,
    playlist,
    track,
    user,
    video,    
)
