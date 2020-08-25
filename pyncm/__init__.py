'''Manages api sessions and calls'''

from .utils.crypto import Crypto
from typing import Any, MutableMapping, Optional, Text, Type, Union
import requests,logging,time

class Session(requests.Session):   
    '''Represents an API session

    Args:
        requests ([type]): [description]

    Returns:
        [type]: [description]
    '''
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
        self.login_info = {'success': False,'tick': time.time(), 'content': None}
        self.csrf_token = ''

    def request(self, method: str, url: Union[str, bytes, Text], *a,**k) -> requests.Response:
        '''Initiates & fires a request

        Args:
            method (str): [HTTP Verb]
            url (Union[str, bytes, Text]): [Full / partial API URL]

        Returns:
            requests.Response: [A requests.Response object]
        '''
        if url[:4] != 'http':url = Session.HOST + url
        return super().request(method,url,*a,**k)             

class SessionManager():
    '''Manages session switching'''
    def __init__(self) -> None:
        self.session = Session()
    def get(self):
        return self.session
    def set(self,session):
        self.session = session

logger = logging.getLogger('ncm')
'''Logger to be used by local modules'''
sessionManager    = SessionManager()
'''Manages active session'''
GetCurrentSession = sessionManager.get
'''Retrives current active session'''
SetCurrentSession = sessionManager.set
'''Sets current active session'''
from .apis import *