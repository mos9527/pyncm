# -*- coding: utf-8 -*-
"""PyNCM-Async 网易云音乐 Python 异步 API / 下载工具"""
__VERSION_MAJOR__ = 0
__VERSION_MINOR__ = 1
__VERSION_PATCH__ = 3

__version__ = "%s.%s.%s" % (__VERSION_MAJOR__, __VERSION_MINOR__, __VERSION_PATCH__)


from threading import current_thread
from typing import Text, Union
from time import time
from .utils.crypto import EapiEncrypt, EapiDecrypt, HexCompose
import logging
import json
import os
import httpx

logger = logging.getLogger("pyncm.api")
if "PYNCM_DEBUG" in os.environ:
    debug_level = os.environ["PYNCM_DEBUG"].upper()
    if not debug_level in {"CRITICAL", "DEBUG", "ERROR", "FATAL", "INFO", "WARNING"}:
        debug_level = "DEBUG"
    logging.basicConfig(
        level=debug_level, format="[%(levelname).4s] %(name)s %(message)s"
    )

DEVICE_ID_DEFAULT = "pyncm!"
# This sometimes fails with some strings, for no particular reason. Though `pyncm!` seem to work everytime..?
# Though with this, all pyncm users would then be sharing the same device Id.
# Don't think that would be of any issue though...
"""默认 deviceID"""
SESSION_STACK = dict()


class Session(httpx.AsyncClient):
    """
    Session

    实现网易云音乐登录态 / API 请求管理

    - HTTP方面，`Session`的配置方法和 `httpx.AsyncClient` 完全一致，如配置 Headers:

    GetCurrentSession().headers['X-Real-IP'] = '1.1.1.1'

    - 该 Session 其他参数也可被修改:

    GetCurrentSession().force_http = True # 优先 HTTP

    - Session 对象本身可作为 Context Manager 使用:

    ```python
    # 利用全局 Session 完成该 API Call
    await LoginViaEmail(...)
    async with CreateNewSession(): # 建立新的 Session，并进入该 Session, 在 `with` 内的 API 将由该 Session 完成
        await LoginViaCellPhone(...)
    # 离开 Session. 此后 API 将继续由全局 Session 管理
    ```
    注：Session 各*线程*独立，各线程利用 `with` 设置的 Session 不互相影响
    注：Session 离开 with clause 时，Session 会被销毁，但不会影响全局 Session
    注：Session 生命周期细节请参阅 https://www.python-httpx.org/async/

    获取其他具体信息请参考该文档注释
    """

    HOST = "music.163.com"
    # 网易云音乐 API 服务器域名，可直接改为代理服务器之域名
    UA_DEFAULT = (
        "Mozilla/5.0 (linux@github.com/mos9527/pyncm) Chrome/PyNCM.%s" % __version__
    )
    # Weapi 使用的 UA
    UA_EAPI = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154"
    # EAPI 使用的 UA，不推荐更改
    UA_LINUX_API = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"
    # 曾经的 Linux 客户端 UA，不推荐更改
    force_http = False
    # 优先使用 HTTP 作 API 请求协议

    async def __aenter__(self) -> httpx.AsyncClient:
        SESSION_STACK.setdefault(current_thread(), list())
        SESSION_STACK[current_thread()].append(self)
        return await super().__aenter__()

    async def __aexit__(self, *args) -> None:
        SESSION_STACK[current_thread()].pop()
        return await super().__aexit__(*args)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": self.UA_DEFAULT,
            "Referer": self.HOST,
        }
        self.login_info = {"success": False, "tick": time(), "content": None}
        self.eapi_config = {
            "os": "ios",
            "appver": "9.0.0",
            "osver": "",
            "deviceId": DEVICE_ID_DEFAULT,
        }
        self.csrf_token = ""

    # region Shorthands
    @property
    def deviceId(self):
        """设备 ID"""
        return self.eapi_config["deviceId"]

    @deviceId.setter
    def deviceId(self, v):
        self.eapi_config["deviceId"] = str(v)

    @property
    def uid(self):
        """用户 ID"""
        return self.login_info["content"]["account"]["id"] if self.logged_in else 0

    @property
    def nickname(self):
        """登陆用户的昵称"""
        return (
            self.login_info["content"]["profile"]["nickname"] if self.logged_in else ""
        )

    @property
    def lastIP(self):
        """登陆时，上一次登陆的 IP"""
        return (
            self.login_info["content"]["profile"]["lastLoginIP"]
            if self.logged_in
            else ""
        )

    @property
    def vipType(self):
        """账号 VIP 等级"""
        return self.login_info["content"]["profile"]["vipType"] if self.logged_in else 0

    @property
    def logged_in(self):
        """是否已经登陆"""
        return self.login_info["success"]

    # endregion
    async def request(
        self, method: str, url: Union[str, bytes, Text], *args, **kwargs
    ) -> httpx.Response:
        """发起 HTTP(S) 请求
        该函数与 `httpx.AsyncClient.request` 有以下不同：
        - 使用 SSL 与否取决于 `force_http`
        - 不强调协议（只用 HTTP(S)），不带协议的链接会自动补上 HTTP(S)

        Args:
            method (str): HTTP Verb
            url (Union[str, bytes, Text]): Complete/Partial HTTP URL

        Returns:
            requests.Response
        """
        if url[:4] != "http":
            url = "https://%s%s" % (self.HOST, url)
        if self.force_http:
            url = url.replace("https:", "http:")
        return await super().request(method, url, *args, **kwargs)

    # Symbols for loading/reloading authentication info
    _session_info = {
        "eapi_config": (
            lambda self: getattr(self, "eapi_config"),
            lambda self, v: setattr(self, "eapi_config", v),
        ),
        "login_info": (
            lambda self: getattr(self, "login_info"),
            lambda self, v: setattr(self, "login_info", v),
        ),
        "csrf_token": (
            lambda self: getattr(self, "csrf_token"),
            lambda self, v: setattr(self, "csrf_token", v),
        ),
        "cookies": (
            lambda self: [
                {"name": c.name, "value": c.value, "domain": c.domain, "path": c.path}
                for c in getattr(getattr(self, "cookies"), "jar")
            ],
            lambda self, cookies: [
                getattr(self, "cookies").set(**cookie) for cookie in cookies
            ],
        ),
    }

    def dump(self) -> dict:
        """以 `dict` 导出登录态"""
        return {
            name: self._session_info[name][0](self)
            for name in self._session_info.keys()
        }

    def load(self, dumped):
        """从 `dict` 加载登录态"""
        for k, v in dumped.items():
            self._session_info[k][1](self, v)
        return True


class SessionManager:
    """PyNCM Session 单例储存对象"""

    def __init__(self) -> None:
        self.session = Session()

    def get(self):
        if SESSION_STACK.get(current_thread(), None):
            return SESSION_STACK[current_thread()][-1]
        return self.session

    def set(self, session):
        if SESSION_STACK.get(current_thread(), None):
            raise Exception(
                "Current Session is in `with` block, which cannot be reassigned."
            )
        self.session = session

    # Session serialization
    @staticmethod
    def stringify_legacy(session: Session) -> str:
        """（旧）序列化 `Session` 为 `str`"""
        return EapiEncrypt("pyncm", json.dumps(session.dump()))["params"]

    @staticmethod
    def parse_legacy(dump: str) -> Session:
        """（旧）反序列化 `str` 为 `Session`"""
        session = Session()
        dump = HexCompose(dump)
        dump = EapiDecrypt(dump).decode()
        dump = dump.split("-36cd479b6b5-")
        assert dump[0] == "pyncm"  # check magic
        session.load(json.loads(dump[1]))  # loading config dict
        return session

    @staticmethod
    def stringify(session: Session) -> str:
        """序列化 `Session` 为 `str`"""
        from json import dumps
        from zlib import compress
        from base64 import b64encode

        return "PYNCM" + b64encode(compress(dumps(session.dump()).encode())).decode()

    @staticmethod
    def parse(dump: str) -> Session:
        """反序列化 `str` 为 `Session`"""
        if (
            dump[:5] == "PYNCM"
        ):  # New marshaler (compressed,base64 encoded) has magic header
            from json import loads
            from zlib import decompress
            from base64 import b64decode

            session = Session()
            session.load(loads(decompress(b64decode(dump[5:])).decode()))
            return session
        else:
            return SessionManager.parse_legacy(dump)


sessionManager = SessionManager()


def GetCurrentSession() -> Session:
    """获取当前正在被 PyNCM 使用的 Session / 登录态"""
    return sessionManager.get()


def SetCurrentSession(session: Session):
    """设置当前正在被 PyNCM 使用的 Session / 登录态"""
    sessionManager.set(session)


def SetNewSession():
    """设置新的被 PyNCM 使用的 Session / 登录态"""
    sessionManager.set(Session())


def CreateNewSession() -> Session:
    """创建新 Session 实例"""
    return Session()


def LoadSessionFromString(dump: str) -> Session:
    """从 `str` 加载 Session / 登录态"""
    session = SessionManager.parse(dump)
    return session


def DumpSessionAsString(session: Session) -> str:
    """从 Session / 登录态 导出 `str`"""
    return SessionManager.stringify(session)
