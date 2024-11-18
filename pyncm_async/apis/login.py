# -*- coding: utf-8 -*-
"""登录、CSRF 有关 APIs"""
from base64 import b64encode
from . import (
    EapiCryptoRequest,
    WeapiCryptoRequest,
    GetCurrentSession,
    logger,
    LoginFailedException,
)
from ..utils.crypto import HashHexDigest
from ..utils.security import cloudmusic_dll_encode_id
import time


def WriteLoginInfo(response, session):
    """写登录态入Session

    Args:
        response (dict): 解码后的登录态

    Raises:
        LoginFailedException: 登陆失败时发生
    """
    session.login_info = {"tick": time.time(), "content": response}
    if not session.login_info["content"]["code"] == 200:
        session.login_info["success"] = False
        raise LoginFailedException(session.login_info["content"])
    session.login_info["success"] = True
    session.csrf_token = session.cookies.get("__csrf")


@WeapiCryptoRequest
def LoginLogout():
    """网页端 - 登出账号

    Returns:
        dict
    """
    return "/weapi/logout", {}


@EapiCryptoRequest
def LoginRefreshToken():
    """网页端 - 刷新登录令牌

    Returns:
        dict
    """
    return "/eapi/login/token/refresh", {}


@WeapiCryptoRequest
def LoginQrcodeUnikey(dtype=1):
    """网页端 - 获取二维码登录令牌

    - 该令牌UUID适用于以下 URL：
     - music.163.com/login?codekey={UUID}
    - 若需要使用该URL，应由网易云音乐移动客户端扫描其二维码 - 链接不会触发入口
    - 登录态将在 `LoginQrcodeCheck` 中更新，需周期性检测

    Args:
        type (int, optional): 未知. Defaults to 1.

    Returns:
        dict
    """
    return "/weapi/login/qrcode/unikey", {"type": str(dtype)}


@WeapiCryptoRequest
def LoginQrcodeCheck(unikey, type=1):
    """网页端 - 二维码登录状态检测

    Args:
        key (str): 二维码 unikey
        type (int, optional): 未知. Defaults to 1.

    Returns:
        dict
    """
    return "/weapi/login/qrcode/client/login", {"key": str(unikey), "type": type}


@WeapiCryptoRequest
def LoginTypeSwitch():
    """网页端 - 用户登出

    Returns:
        dict
    """
    return "/weapi/logout", {}


@WeapiCryptoRequest
def GetCurrentLoginStatus():
    """网页端 - 获取当前登录态

    Returns:
        dict
    """
    return "/weapi/w/nuser/account/get", {}


async def LoginViaCookie(MUSIC_U="", **kwargs):
    """通过 Cookie 登陆

    Args:
        MUSIC_U (str, optional): Cookie 中的 MUSIC_U. Defaults to ''.

    Returns:
        dict
    """
    session = GetCurrentSession()
    session.cookies.update({"MUSIC_U": MUSIC_U, **kwargs})
    resp = await GetCurrentLoginStatus()
    WriteLoginInfo(resp, session)
    return {"code": 200, "result": session.login_info}


async def LoginViaCellphone(
    phone="",
    password="",
    passwordHash="",
    captcha="",
    ctcode=86,
    remeberLogin=True,
    session=None,
) -> dict:
    """PC 端 - 手机号登陆

    * 若同时指定 password 和 passwordHash, 优先使用 password
    * 若同时指定 captcha 与 password, 优先使用 captcha

    Args:
        phone (str, optional): 手机号. Defaults to ''.
        countrycode (int, optional): 国家代码. Defaults to 86.
        remeberLogin (bool, optional): 是否‘自动登录’，设置 `False` 可能导致权限问题. Defaults to True.
        * 以下验证方式有 1 个含参即可
        password (str, optional): 明文密码. Defaults to ''.
        passwordHash (str, optional): 密码md5哈希. Defaults to ''.
        captcha (str, optional): 手机验证码. 需要已在同一 Session 中发送过 SetSendRegisterVerifcationCodeViaCellphone. Defaults to ''.

    Raises:
        LoginFailedException: 登陆失败时发生

    Returns:
        dict
    """
    path = "/eapi/w/login/cellphone"
    session = session or GetCurrentSession()
    if password:
        passwordHash = HashHexDigest(password)

    if not (passwordHash or captcha):
        raise LoginFailedException("未提供密码或验证码")

    auth_token = (
        {"password": str(passwordHash)} if not captcha else {"captcha": str(captcha)}
    )

    login_status = await EapiCryptoRequest(
        lambda: (
            path,
            {
                "type": "1",
                "phone": str(phone),
                "remember": str(remeberLogin).lower(),
                "countrycode": str(ctcode),
                "checkToken": "",
                **auth_token,
            },
        )
    )(session=session)

    WriteLoginInfo(login_status, session)
    return {"code": 200, "result": session.login_info}


async def LoginViaEmail(
    email="", password="", passwordHash="", remeberLogin=True, session=None
) -> dict:
    """网页端 - 邮箱登陆

    * 若同时指定 password 和 passwordHash, 优先使用 password

    Args:
        email (str, optional): 邮箱地址. Defaults to ''.
        remeberLogin (bool, optional): 是否‘自动登录’，设置 `False` 可能导致权限问题. Defaults to True.
        * 以下验证方式有 1 个含参即可
        password (str, optional): 明文密码. Defaults to ''.
        passwordHash (str, optional): 密码md5哈希. Defaults to ''.

    Raises:
        LoginFailedException: 登陆失败时发生

    Returns:
        dict
    """
    path = "/eapi/login"
    session = session or GetCurrentSession()
    if password:
        passwordHash = HashHexDigest(password)

    if not passwordHash:
        raise LoginFailedException("未提供密码")

    auth_token = {"password": str(passwordHash)}

    login_status = await EapiCryptoRequest(
        lambda: (
            path,
            {
                "type": "1",
                "username": str(email),
                "remember": str(remeberLogin).lower(),
                **auth_token,
            },
        )
    )(session=session)

    WriteLoginInfo(login_status, session)
    return {"code": 200, "result": session.login_info}


async def LoginViaAnonymousAccount(deviceId=None, session=None):
    """PC 端 - 游客登陆

    Args:
        deviceId (str optional): 设备 ID. 设置非 None 将同时改变 Session 的设备 ID. Defaults to None.

    Notes:
        Session 默认使用 `pyncm!` 作为设备 ID

    Returns:
        dict
    """
    session = session or GetCurrentSession()
    if not deviceId:
        deviceId = session.deviceId
    login_status = WeapiCryptoRequest(
        lambda: (
            "/api/register/anonimous",
            {
                "username": b64encode(
                    ("%s %s" % (deviceId, cloudmusic_dll_encode_id(deviceId))).encode()
                ).decode()
            },
        )
    )(session=session)
    assert login_status["code"] == 200, "匿名登陆失败"
    WriteLoginInfo(
        {
            **login_status,
            "profile": {"nickname": "Anonymous", **login_status},
            "account": {"id": login_status["userId"], **login_status},
        },
        session,
    )
    return session.login_info


@WeapiCryptoRequest
def SetSendRegisterVerifcationCodeViaCellphone(cell: str, ctcode=86):
    """网页端 - 发送验证码

    - 验证码 24h 内最多发送五次

    Args:
        cell (str): 手机号
        ctcode (int, optional): 国家代码. Defaults to 86.

    Returns:
        dict
    """
    return "/weapi/sms/captcha/sent", {"cellphone": str(cell), "ctcode": ctcode}


@WeapiCryptoRequest
def GetRegisterVerifcationStatusViaCellphone(cell: str, captcha: str, ctcode=86):
    """网页端 - 检查验证码是否正确

    Args:
        cell (str): 手机号
        captcha (str): 验证码
        ctcode (int, optional): 国家代码. Defaults to 86.

    Returns:
        dict
    """
    return "/weapi/sms/captcha/verify", {
        "cellphone": str(cell),
        "captcha": str(captcha),
        "ctcode": ctcode,
    }


@WeapiCryptoRequest
def SetRegisterAccountViaCellphone(
    cell: str, captcha: str, nickname: str, password: str
):
    """网页端 - 手机号注册

    - 需要已通过 `SetSendRegisterVerifcationCodeViaCellphone` 发送验证码
    - `忘记密码` 同样使用该 API
    - 成功后，现`Session`将登陆进入该账号

    Args:
        cell (str): 手机号
        captcha (str): 验证码
        nickname (str): 昵称
        password (str): 密码

    Returns:
        dict
    """
    return "/weapi/w/register/cellphone", {
        "captcha": str(captcha),
        "nickname": str(nickname),
        "password": HashHexDigest(password),
        "phone": str(cell),
    }


@EapiCryptoRequest
def CheckIsCellphoneRegistered(cell: str, prefix=86):
    """移动端 - 检查某手机号是否已注册

    Args:
        cell (str): 手机号
        prefix (int): 区号 . Defaults to 86

    Returns:
        dict
    """
    return "/eapi/cellphone/existence/check", {"cellphone": cell, "countrycode": prefix}
