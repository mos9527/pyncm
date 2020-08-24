from .. import GetCurrentSession
from .. import logger
from ..crypto import Crypto
import json

class LoginRequiredException(Exception):pass
class LoginFailedException(Exception):pass
# region Base models export
def BaseCryptoRequest(crypto):
    '''Base cryptographic request maker'''
    def preWrapper(func):
        def wrapper(*a,**k):
            url,plain = func(*a,**k)
            if isinstance(plain,dict):
                plain = json.dumps({**plain,'csrf_token':GetCurrentSession().csrf_token})
            if not isinstance(plain,str):plain = str(plain)
            # done converting,let's go
            payload = crypto(url,plain)
            req = GetCurrentSession().post(
                GetCurrentSession().HOST + url,
                params={'csrf_token':GetCurrentSession().csrf_token},
                data={
                    **payload
                }
            )
            rsp = req.text
            try:
                return json.loads(rsp)
            except json.JSONDecodeError:
                return rsp
        return wrapper
    return preWrapper

def WeapiCryptoRequest(func):
    return BaseCryptoRequest(lambda url,plain:Crypto.WeapiCrypto(plain))(func)

def LapiCryptoRequest(func):
    return BaseCryptoRequest(lambda url,plain:Crypto.LinuxCrypto(plain))(func)

def EapiCryptoRequest(func):
    return BaseCryptoRequest(lambda url,plain:Crypto.EapiCrypto(url,plain))(func)

# endregion

import os
__all__ = [i[:-3] for i in os.listdir(os.path.dirname(__file__)) if i[-2:] == 'py' and i != '__init__.py']
from . import * # import all local modules