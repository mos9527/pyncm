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
from typing import Callable, Coroutine, Any, Union, Dict
from requests.models import Response as SyncResponse
from httpx import Response as AsyncResponse

from .exception import LoginRequiredException
from ..utils.crypto import (
    EapiDecrypt,
    EapiEncrypt,
    WeapiEncrypt,
    AbroadDecrypt,
)
from .. import GetCurrentSession, logger, Session, ASYNC_MODE
import json, urllib.parse


LOGIN_REQUIRED = LoginRequiredException("需要登录")


def _BaseWrapper(requestFunc) -> Callable[..., Union[Dict[str, Any], str, Coroutine[Any, Any, Union[Dict[str, Any], str]]]]:
    """API加密函数通用修饰器

    实际使用请参考以下其他 Wrapper::
        
        UserIDBasedApi
        WeapiCryptoRequest
        LapiCryptoRequest
        EapiCryptoRequest
    """

    @wraps(requestFunc)
    def apiWrapper(apiFunc):
        def _execute_request(*a, **k) -> Union[SyncResponse, Coroutine[Any, Any, AsyncResponse]]:
            # HACK: 'session=' keyword support
            session = k.get("session", GetCurrentSession())
            # HACK: For now,wrapped functions will not have access to the session object
            if "session" in k:
                del k["session"]

            ret = apiFunc(*a, **k)
            url, payload = ret[:2]
            method = ret[-1] if ret[-1] in ["POST", "GET"] else "POST"
            logger.debug(
                "TYPE=%s API=%s.%s %s url=%s deviceId=%s payload=%s session=0x%x"
                % (
                    requestFunc.__name__.split("Crypto")[0].upper(),
                    apiFunc.__module__,
                    apiFunc.__name__,
                    method,
                    url,
                    session.deviceId,
                    payload,
                    id(session),
                )
            )
            return requestFunc(session, url, payload, method)

        def _parse_rsp(rsp: Union[SyncResponse, AsyncResponse]) -> Union[dict, str]:
            try:
                payload = rsp.text if isinstance(rsp, (SyncResponse, AsyncResponse)) else rsp
                payload = payload.decode() if not isinstance(payload, str) else payload
                payload = json.loads(payload.strip("\x10"))
                if "abroad" in payload and payload["abroad"]:
                    # Addresses Issue #15
                    # This however, has some unforeseen side-effects. Mainly due to its diffrences
                    # with non-abraod responses.
                    logger.warn(
                        'Detected "abroad" payload. API response might differ in format!'
                    )
                    real_payload = AbroadDecrypt(payload["result"])
                    payload = {"result": json.loads(real_payload)}
                    # We'll let the user know about it
                    payload["abroad"] = True
                return payload
            except json.JSONDecodeError as e:
                logger.error("Response is not valid JSON : %s" % e)
                logger.error("Response : %s", rsp)
                return rsp

        @wraps(apiFunc)
        async def async_wrapper(*a, **k):
            rsp = await _execute_request(*a, **k)
            return _parse_rsp(rsp)

        @wraps(apiFunc)
        def sync_wrapper(*a, **k):
            rsp = _execute_request(*a, **k)
            return _parse_rsp(rsp)

        return async_wrapper if ASYNC_MODE else sync_wrapper

    return apiWrapper


def EapiEncipered(func):
    """函数值有 Eapi 加密 - 解密并返回原文"""

    @wraps(func)
    def wrapper(*a, **k):
        payload = func(*a, **k)
        try:
            return EapiDecrypt(payload).decode()
        except:
            return payload

    return wrapper


@_BaseWrapper
def WeapiCryptoRequest(session: "Session", url, plain, method="POST"):
    """Weapi - 适用于 网页端、小程序、手机端部分 APIs"""
    payload = json.dumps({**plain, "csrf_token": session.csrf_token})
    return session.request(
        method,
        url.replace("/api/", "/weapi/"),
        params={"csrf_token": session.csrf_token},
        data={**WeapiEncrypt(payload)},
        headers={"User-Agent": session.UA_DEFAULT, "Referer": "https://music.163.com"},
        cookies={**session.eapi_config},
    )


# 来自 https://github.com/Binaryify/NeteaseCloudMusicApi
def _EapiCryptoRequest(func):
    def _execute_request(session: "Session", url, plain, method) -> Callable[..., Union[Dict[str, Any], str, Coroutine[Any, Any, Union[Dict[str, Any], str]]]]:
        payload = {
            **plain,
            "header": json.dumps(
                {**session.eapi_config, "requestId": str(randrange(20000000, 30000000))}
            ),
        }
        digest = EapiEncrypt(
            urllib.parse.urlparse(url).path.replace("/eapi/", "/api/"), json.dumps(payload)
        )
        return session.request(
            method, 
            url, 
            headers={"User-Agent": session.UA_EAPI, "Referer": ""}, 
            cookies={**session.eapi_config}, 
            data={**digest}, 
        )

    def _parse_rsp(rsp: Union[SyncResponse, AsyncResponse]):
        payload = rsp.content
        try:
            return EapiDecrypt(payload).decode()
        except:
            return payload

    # @wraps(func)
    def sync_wrapper(session: "Session", url, plain, method):
        rsp = _execute_request(session, url, plain, method)
        return _parse_rsp(rsp)
    
    # @wraps(func)
    async def async_wrapper(session: "Session", url, plain, method):
        rsp = await _execute_request(session, url, plain, method)
        return _parse_rsp(rsp)
    
    return async_wrapper if ASYNC_MODE else sync_wrapper

@_BaseWrapper
@EapiEncipered
@_EapiCryptoRequest
def EapiCryptoRequest(session: "Session", url, plain, method):
    """Eapi - 适用于新版客户端绝大部分API"""
    ...


# 注：向后支持；文档允许从`apis`直接导入这些子模块
from . import (
    artist as artist,
    miniprograms as miniprograms,
    album as album,
    cloud as cloud,
    cloudsearch as cloudsearch,
    login as login,
    playlist as playlist,
    track as track,
    user as user,
    video as video,
)
