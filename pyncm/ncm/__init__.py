'''
# Netease Cloud Music Core

Core class for handling NCM API Calls
'''

from pyncm.ncm.crypto import Crypto
from typing import Type
import requests,logging,time

class Session(requests.Session):
    '''
        # Session module
        Stores config and requests. Important things are at `apis`,take a look there
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
        self.verify = False
        
        
class SessionManager():
    # How to abuse mutable types (((gone wild)))
    def __init__(self) -> None:
        self.session = Session()
    def get(self):
        return self.session
    def set(self,session):
        self.session = session

logger = logging.getLogger('ncm')
sessionManager    = SessionManager()
GetCurrentSession = sessionManager.get
SetCurrentSession = sessionManager.set
from .apis import *
