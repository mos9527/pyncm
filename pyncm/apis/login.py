'''登录、CSRF 有关 APIs'''
from . import EapiCryptoRequest, WeapiCryptoRequest,GetCurrentSession,logger,Crypto,LoginFailedException
import time
def LoginViaCellphone(phone='', password='',remeberLogin=True) -> dict:
    '''网页端 - 手机号登陆

    Args:
        phone (str, optional): 手机号. Defaults to ''.
        password (str, optional): 明文密码. Defaults to ''.
        remeberLogin (bool, optional): 是否‘自动登录’，开启可延长 CSRF 令牌时效. Defaults to True.

    Raises:
        LoginFailedException: 当登陆失败时发生

    Returns:
        dict
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
    '''检查某手机号是否已注册

    Args:
        cell (str): 手机号
        prefix (int): 区号 . Defaults to 86

    Returns:
        dict
    '''
    return '/eapi/cellphone/existence/check',{'cellphone':cell,'countrycode':prefix}