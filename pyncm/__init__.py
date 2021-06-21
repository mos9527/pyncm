'''# pyncm
本模块提供`Get/Set/DumpCurrentSession`,`LoadNewSessionFromDump` 以管理请求
API 使用请参见 `pyncm.apis` 文档 
'''

from .utils.crypto import Crypto
from typing import Text, Union
from time import time
import requests,logging,json

__version__ = "1.6.3.7"

class Session(requests.Session):   
    '''Represents an API session'''
    HOST          = "https://music.163.com/"
    UA_DEFAULT    = 'Mozilla/5.0 (linux@github.com/greats3an/pyncm) Chrome/But.It.Was.Actually.PyNCM.%s' % __version__ # XXX this is just stupid
    UA_EAPI       = 'NeteaseMusic/7.2.24.1597753235(7002024);Dalvik/2.1.0 (Linux; U; Android 11; Pixel 2 XL Build/RP1A.200720.009)'
    UA_LINUX_API  = 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36'    
    CONFIG_EAPI   = {
        # template EAPI config pulled from version 7.2.24, which would be overriden if some of the keys were specified in cookies 
        'appver': '7.2.24','buildver':'7002024','channel':'offical','deviceId': Crypto.RandomString(8),
        'mobilename' : 'Pixel2XL','os': 'android','osver':'10.1','resolution': '2712x1440','versioncode': '240'         
    }

    def __init__(self,*a,**k):        
        super().__init__(*a,**k)
        self.headers = {
            "Content-Type"  : "application/x-www-form-urlencoded",  
            "User-Agent"    : self.UA_DEFAULT,
            "Referer"       : self.HOST
        }
        self.login_info = {'success': False,'tick': time(), 'content': None}
        self.csrf_token = ''

    def request(self, method: str, url: Union[str, bytes, Text], *a,**k) -> requests.Response:
        '''Initiates & fires a request

        Args:
            method (str): HTTP Verb
            url (Union[str, bytes, Text]): Full / partial API URL

        Returns:
            requests.Response: A requests.Response object
        '''    
        if url[:4] != 'http':url = self.HOST + url                
        return super().request(method,url,*a,**k)  

    # region auth IO
    _AUTH_SYMBOLS = {
        # symbols for loading/reloading authentication info
        'login_info':(lambda self:getattr(self,'login_info'),lambda self,v:setattr(self,'login_info',v)),
        'csrf_token':(lambda self:getattr(self,'csrf_token'),lambda self,v:setattr(self,'csrf_token',v)),
        'cookies':   (
            lambda self:
                [{'name': c.name, 'value': c.value, 'domain': c.domain, 'path': c.path} for c in getattr(self,'cookies')],
            lambda self,cookies:
                [getattr(self,'cookies').set(**cookie) for cookie in cookies]
        )
    }
    def dump(self) -> dict:
        '''Dumps current authencation info as dictionary'''
        return {name:self._AUTH_SYMBOLS[name][0](self) for name in self._AUTH_SYMBOLS.keys()}
    def load(self,dumped):
        '''Loads current authencation info from dictionary'''
        for k,v in dumped.items():self._AUTH_SYMBOLS[k][1](self,v)
        return True
    # endregion 

class SessionManager():
    '''Manages session switching / loading / dumping'''
    def __init__(self) -> None:
        self.session = Session()
    def get(self):
        return self.session
    def set(self,session):
        self.session = session
    # region Session serialization
    @staticmethod
    def stringify(session : Session) -> str:
        return Crypto.EapiCrypto('pyncm',json.dumps(session.dump()))['params']
    @staticmethod
    def parse(dump : str) -> Session:
        session = Session() # a new session WILL be created
        dump = Crypto.HexCompose(dump)
        dump = Crypto.EapiDecrypt(dump).decode()
        dump = dump.split('-36cd479b6b5-')
        assert dump[0] == 'pyncm' # check magic
        session.load(json.loads(dump[1])) # loading config dict in
        return session
    # endregion
       
logger = logging.getLogger('ncm')
'''Logger to be used by local modules'''
sessionManager              = SessionManager()
'''Manages active session'''
def GetCurrentSession() -> Session:
    '''Retrives current active session'''
    return sessionManager.get()
def SetCurrentSession(session : Session):
    '''Sets current active session'''
    sessionManager.set(session)
def SetNewSession():
    '''Creates and sets new session'''
    sessionManager.set(Session())
def LoadSessionFromString(dump : str) -> Session:
    '''Loads a session from dumped string'''
    session = SessionManager.parse(dump)
    return session
def DumpSessionAsString(session : Session) -> str:
    '''Dumps session as encrypted string'''
    return SessionManager.stringify(session)
from .apis import *