'''Login / CSRF forgery related APIs'''
from . import EapiCryptoRequest, WeapiCryptoRequest,GetCurrentSession,logger,Crypto,LoginFailedException
import time
def LoginViaCellphone(phone='', password='',remeberLogin=True) -> dict:
    '''Logging in with your phone & password (used in web version)

    Args:
        phone (str, optional): Phone number. Defaults to ''.
        password (str, optional): Plaintext password. Defaults to ''.
        remeberLogin (bool, optional): Cookies will remain valid for longer. Defaults to True.

    Raises:
        LoginFailedException: Raises when failed to authenticate

    Returns:
        dict: Your nickname,UID,etc
    '''
    sess = GetCurrentSession()
    if (phone and password):
        sess.phone = phone
        sess.password = password
        LoginViaCellphone()
    else:
        if (sess.phone and sess.password):
            md5_password = Crypto.HashDigest(sess.password)
            r = WeapiCryptoRequest(lambda:('/weapi/login/cellphone',{"phone":str(sess.phone),"password":str(md5_password),"rememberLogin":str(remeberLogin).lower(),"checkToken":""}))()
            sess.login_info = {'tick': time.time(), 'content':r}
            if not sess.login_info['content']['code'] == 200:
                sess.login_info['success'] = False
                raise LoginFailedException(sess.login_info['content'])
            sess.login_info['success'] = True
            cookie = sess.cookies.get_dict()
            sess.csrf_token = cookie['__csrf']
            logger.debug('Updated login info for user %s' % sess.login_info['content']['profile']['nickname'])
            return sess.login_info
        else:
            raise LoginFailedException('Not enough login info provided')

@EapiCryptoRequest
def CheckIsCellphoneRegistered(cell : str,prefix=86):
    '''Check if a phone number has already registered

    Args:
        cell (str): Phone number
        prefix (int): Loaction prefix . Defaults to 86

    Returns:
        dict : Cell's registeration status
    '''
    return '/eapi/cellphone/existence/check',{'cellphone':cell,'countrycode':prefix}