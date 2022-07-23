# -*- coding: utf-8 -*-
"""PyNCM 网易云音乐 Python API / 下载工具

PyNCM 包装的网易云音乐 API 的使用非常简单::
    
    >>> from pyncm import apis
    # 登录
    >>> apis.LoginViaCellphone(phone="[..]", password="[..]", ctcode=86, remeberLogin=True)
    # 获取歌曲信息    
    >>> apis.track.GetTrackAudio(29732235)
    {'data': [{'id': 29732235, 'url': 'http://m701.music...
    # 获取歌曲详情
    >>> apis.track.GetTrackDetail(29732235)    
    {'songs': [{'name': 'Supernova', 'id': 2...
    # 获取歌曲评论
    >>> apis.track.GetTrackComments(29732235)    
    {'isMusician': False, 'userId': -1, 'topComments': [], 'moreHot': True, 'hotComments': [{'user': {'locationInfo': None, 'liveIn ...

PyNCM 的所有 API 请求都将经过单例的 `pyncm.Session` 发出，管理此单例可以使用::

    >>> session = pyncm.GetCurrentSession()
    >>> pyncm.SetCurrentSession(session)
    >>> pyncm.SetNewSession()

PyNCM 同时提供了相应的 Session 序列化函数，用于其储存及管理::

    >>> save = pyncm.DumpSessionAsString()
    >>> pyncm.SetNewSession(
            pyncm.LoadSessionFromString(save)
        )

# 注意事项
    - (PR#11) 海外用户可能经历 460 "Cheating" 问题，可通过添加以下 Header 解决: `X-Real-IP = 118.88.88.88`    
"""
from typing import Text, Union
from time import time
from .utils.crypto import RandomString, EapiEncrypt, EapiDecrypt, HexCompose
import requests, logging, json
logger = logging.getLogger("pyncm")

__version__ = "1.6.6.7"

class Session(requests.Session):
    """# Session
    实现网易云音乐登录态 / API请求管理

    - HTTP方面，`Session`的配置方法和 `requests.Session` 完全一致，如配置 Headers::

    GetCurrentSession().headers['X-Real-IP'] = '1.1.1.1'

    - 该 Session 其他参数也可被修改::

    GetCurrentSession().force_http = True # 优先 HTTP

    获取其他具体信息请参考该文档注释
    """
    
    force_http = False
    """优先使用 HTTP 作 API 请求协议"""
    
    # region Consts
    HOST = "music.163.com"
    """网易云音乐 API 服务器域名，可直接改为代理服务器之域名"""
    UA_DEFAULT = (
        "Mozilla/5.0 (linux@github.com/mos9527/pyncm) Chrome/PyNCM.%s" % __version__        
    )
    """Weapi 使用的 UA"""
    UA_EAPI = "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Safari/537.36 Chrome/91.0.4472.164 NeteaseMusicDesktop/2.10.2.200154"
    """EAPI 使用的 UA，不推荐更改"""
    UA_LINUX_API = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"
    """曾经的 Linux 客户端 UA，不推荐更改"""
    CONFIG_EAPI = {
        "os": "pc",
        "appver": "",
        "osver": "",
        "deviceId": '',
    }
    """EAPI 额外请求头（在 Cookies 中）"""
    # endregion

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": self.UA_DEFAULT,
            "Referer": self.HOST,
        }
        self.login_info = {"success": False, "tick": time(), "content": None}
        self.csrf_token = ""

    # region Shorthands
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
    def request(
        self, method: str, url: Union[str, bytes, Text], *a, **k
    ) -> requests.Response:
        """发起 HTTP(S) 请求
        该函数与 `requests.Session.request` 有以下不同：
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
        return super().request(method, url, *a, **k)

    # region symbols for loading/reloading authentication info
    _session_info = {
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
                for c in getattr(self, "cookies")
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

    # endregion


class SessionManager:
    """PyNCM Session 单例储存对象"""
    def __init__(self) -> None:
        self.session = Session()

    def get(self):
        return self.session

    def set(self, session):
        self.session = session

    # region Session serialization
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
        return 'PYNCM' + b64encode(compress(dumps(session.dump()).encode())).decode()

    @staticmethod
    def parse(dump : str) -> Session:
        """反序列化 `str` 为 `Session`"""
        if dump[:5] == 'PYNCM': # New marshaler (compressed,base64 encoded) has magic header
            from json import loads
            from zlib import decompress
            from base64 import b64decode
            session_obj = Session()
            session_obj.load(loads(decompress(b64decode(dump[5:])).decode()))
        else:
            return SessionManager.parse_legacy(dump)

    # endregion

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


def LoadSessionFromString(dump: str) -> Session:
    """从 `str` 加载 Session / 登录态"""
    session = SessionManager.parse(dump)
    return session


def DumpSessionAsString(session: Session) -> str:
    """从 Session / 登录态 导出 `str`"""
    return SessionManager.stringify(session)
