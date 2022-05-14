# -*- coding: utf-8 -*-
"""# pyncm
本模块提供`Get/Set/DumpCurrentSession`,`LoadNewSessionFromDump` 以管理请求
API 使用请参见 `pyncm.apis` 文档 
"""
from typing import Text, Union
from time import time
from .utils.crypto import RandomString, EapiEncrypt, EapiDecrypt, HexCompose
import requests, logging, json

__version__ = "1.6.6.1"


class Session(requests.Session):
    """Represents an API session"""

    HOST = "music.163.com"
    UA_DEFAULT = (
        "Mozilla/5.0 (linux@github.com/greats3an/pyncm) Chrome/PyNCM.%s" % __version__
    )
    UA_EAPI = "NeteaseMusic/7.2.24.1597753235(7002024);Dalvik/2.1.0 (Linux; U; Android 11; Pixel 2 XL Build/RP1A.200720.009)"
    UA_LINUX_API = "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36"
    CONFIG_EAPI = {
        "appver": "9.9.99",
        "buildver": "9009099",
        "channel": "offical",
        "deviceId": RandomString(8),
        "mobilename": "Pixel2XL",
        "os": "android",
        "osver": "10.1",
        "resolution": "2712x1440",
        "versioncode": "240",
    }
    force_http = False

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
        """Initiates & fires a request

        Args:
            method (str): HTTP Verb
            url (Union[str, bytes, Text]): Full / partial API URL

        Returns:
            requests.Response: A requests.Response object
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
        """Dumps current session info as dictionary"""
        return {
            name: self._session_info[name][0](self)
            for name in self._session_info.keys()
        }

    def load(self, dumped):
        """Loads session info from dictionary"""
        for k, v in dumped.items():
            self._session_info[k][1](self, v)
        return True

    # endregion


class SessionManager:
    """Manages session switching / loading / dumping"""

    def __init__(self) -> None:
        self.session = Session()

    def get(self):
        return self.session

    def set(self, session):
        self.session = session

    # region Session serialization
    @staticmethod
    def stringify(session: Session) -> str:
        return EapiEncrypt("pyncm", json.dumps(session.dump()))["params"]

    @staticmethod
    def parse(dump: str) -> Session:
        session = Session()
        dump = HexCompose(dump)
        dump = EapiDecrypt(dump).decode()
        dump = dump.split("-36cd479b6b5-")
        assert dump[0] == "pyncm"  # check magic
        session.load(json.loads(dump[1]))  # loading config dict
        return session

    # endregion


logger = logging.getLogger("ncm")
"""Logger to be used by local modules"""
sessionManager = SessionManager()
"""Manages active session"""


def GetCurrentSession() -> Session:
    """Retrives current active session"""
    return sessionManager.get()


def SetCurrentSession(session: Session):
    """Sets current active session"""
    sessionManager.set(session)


def SetNewSession():
    """Creates and sets new session"""
    sessionManager.set(Session())


def LoadSessionFromString(dump: str) -> Session:
    """Loads a session from dumped string"""
    session = SessionManager.parse(dump)
    return session


def DumpSessionAsString(session: Session) -> str:
    """Dumps session as encrypted string"""
    return SessionManager.stringify(session)
