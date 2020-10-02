'''# pyncm
本模块提供`Get/Set/DumpCurrentSession`,`LoadNewSessionFromDump` 以管理请求
API 使用请参见 `pyncm.apis` 文档'''

from .utils.crypto import Crypto
from typing import Text, Union
from time import time
import requests,logging,json

__version__ = "1.4.1"

class Session(requests.Session):   
    '''Represents an API session'''
    HOST = "https://music.163.com"
    
    def __init__(self,*a,**k):
        # Setting up our request session
        super().__init__(*a,**k)
        self.headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "User-Agent": "mos9527 Him Self/v15",
            "Referer":Session.HOST
        }
        # Setting up default values
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
        if url[:4] != 'http':url = Session.HOST + url
        return super().request(method,url,*a,**k)             
    
    DUMPS = {
        # 'name':(getfunc,setfunc)
        'login_info':(lambda self:getattr(self,'login_info'),lambda self,v:setattr(self,'login_info',v)),
        'csrf_token':(lambda self:getattr(self,'csrf_token'),lambda self,v:setattr(self,'csrf_token',v)),
        'cookies':   (lambda self:getattr(self,'cookies').get_dict(),lambda self,v:getattr(self,'cookies').update(v))
    }
    def dump(self) -> dict:
        '''Dumps partial class variables as dictionary'''
        return {name:Session.DUMPS[name][0](self) for name in Session.DUMPS.keys()}
    def load(self,dumped):
        '''Loads dumped dictioary as class variables'''
        for k,v in dumped.items():Session.DUMPS[k][1](self,v)
        return True

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
sessionManager          = SessionManager()
'''Manages active session'''
GetCurrentSession       = sessionManager.get
'''Retrives current active session'''
SetCurrentSession       = sessionManager.set
'''Sets current active session'''
def LoadSessionFromString(dump : str):
    '''Loads a session from dumped string'''
    session = SessionManager.parse(dump)
    SetCurrentSession(session)
def DumpCurrentSessionAsString():
    '''Dumps current session as encrypted string'''
    return SessionManager.stringify(GetCurrentSession())
from .apis import *