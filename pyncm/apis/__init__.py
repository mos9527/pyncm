# -*- coding: utf-8 -*-
"""网易云音乐 APIs

## 注意事项
- (#11) 海外用户可能经历 460 "Cheating" 问题，可通过添加以下 Header 解决:    
    GetCurrentSession().headers['X-Real-IP'] = '118.88.88.88'

## 新 API
在获得相关 API 路径和参数后(可参考 Binaryify 大佬的视频 - BV1PY41147r9)
可参考已有 API 函数格式编写相关 PyNCM API. 各API模式修饰器已在本文件注释
"""

from time import time
from requests.models import Response
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


# region Base models export
LOGIN_REQUIRED = LoginRequiredException("Function needs you to be logged in")


def parse(url):
    return urllib.parse.urlparse(url)


def BaseWrapper(requestFunc):
    """Base wrapper for crypto requests"""

    def apiWrapper(apiFunc):
        """apiFunc -> rtype : (url,plain,[method])"""

        def wrapper(*a, **k):
            ret = apiFunc(*a, **k)
            url, plain = ret[:2]
            method = ret[-1] if ret[-1] in ["POST", "GET"] else "POST"
            rsp = requestFunc(url, plain, method)
            try:
                payload = rsp.text if isinstance(rsp, Response) else rsp
                payload = payload.decode() if not isinstance(payload, str) else payload
                payload = json.loads(
                    payload.strip("\x10")
                )  # plaintext responses are also padded...
                if "abroad" in payload and payload["abroad"]:  # addresses #15
                    real_payload = AbroadDecrypt(payload["result"])
                    payload = json.loads(real_payload)
                return payload
            except json.JSONDecodeError:
                return rsp

        return wrapper

    return apiWrapper


def LoginRequiredApi(func):
    """API 需要事先登录"""

    def wrapper(*a, **k):
        if not GetCurrentSession().login_info["success"]:
            raise LOGIN_REQUIRED
        return func(*a, **k)

    return wrapper


def UserIDBasedApi(func):
    """API 第一参数为用户 ID，而该参数可留 0 而指代已登录的用户 ID"""

    def wrapper(user_id=0, *a, **k):
        if user_id == 0 and GetCurrentSession().login_info["success"]:
            user_id = GetCurrentSession().uid
        elif user_id == 0:
            raise LOGIN_REQUIRED
        return func(user_id, *a, **k)

    return wrapper


def EapiEncipered(func):
    """函数值有 Eapi 加密 - 解密并返回原文"""

    def wrapper(*a, **k):
        payload = func(*a, **k)
        try:
            return EapiDecrypt(payload).decode()
        except:
            return payload

    return wrapper


@BaseWrapper
def WeapiCryptoRequest(url, plain, method):
    """Weapi - 适用于 网页端、小程序、手机端部分 APIs"""
    payload = json.dumps({**plain, "csrf_token": GetCurrentSession().csrf_token})
    return GetCurrentSession().request(
        method,
        url.replace("/api/", "/weapi/"),
        params={"csrf_token": GetCurrentSession().csrf_token},
        data={**WeapiEncrypt(payload)},
    )


# region Port of `Binaryify/NeteaseCloudMusicApi`
@BaseWrapper
def LapiCryptoRequest(url, plain, method):
    """Linux API - 适用于 Linux 客户端部分 APIs"""
    payload = {"method": method, "url": GetCurrentSession().HOST + url, "params": plain}
    payload = json.dumps(payload)
    return GetCurrentSession().request(
        method,
        "/api/linux/forward",
        headers={"User-Agent": GetCurrentSession().UA_LINUX_API},
        data={**LinuxApiEncrypt(payload)},
    )


@BaseWrapper
@EapiEncipered
def EapiCryptoRequest(url, plain, method):
    """Eapi - 适用于 新版客户端绝大部分 APIs"""
    cookies = {
        **GetCurrentSession().CONFIG_EAPI,
        "requestId": f"{int(time() * 1000)}_0233",
        "__csrf": GetCurrentSession().csrf_token,
        # **GetCurrentSession().cookies,
    }
    payload = {**plain, "header": json.dumps(cookies)}
    request = GetCurrentSession().request(
        method,
        url,
        headers={"User-Agent": GetCurrentSession().UA_EAPI, "Referer": None},
        cookies=cookies,
        data={
            **EapiEncrypt(
                parse(url).path.replace("/eapi/", "/api/"), json.dumps(payload)
            )
        },
    )
    return request.content


# endregion
# endregion
from . import (
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
