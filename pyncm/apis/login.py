'''登录、CSRF 有关 APIs'''
from os import pathsep
from . import EapiCryptoRequest, WeapiCryptoRequest,GetCurrentSession,logger,Crypto,LoginFailedException
import time

@WeapiCryptoRequest
def LoginLogout():
    '''网页端 - 登出账号

    Returns:
        dict
    '''
    return '/weapi/logout',{}

@WeapiCryptoRequest
def LoginRefreshToken():
    '''网页端 - 刷新登录令牌

    Returns:
        dict
    '''
    return '/weapi/w/login/cellphone',{}

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
    path='/weapi/w/login/cellphone'
    sess = GetCurrentSession()
    if (phone and password):
        sess.phone = phone
        sess.password = password
        LoginViaCellphone()
    else:
        if (sess.phone and sess.password):
            md5_password = Crypto.HashDigest(sess.password)
            r = WeapiCryptoRequest(lambda:(path,{
                "phone":str(sess.phone),
                "password":str(md5_password),
                "rememberLogin":str(remeberLogin).lower(),
                "checkToken":"9ca17ae2e6ffcda170e2e6ee97f3648d908ba9fb7c8ab88ab6c54b868e8ebbaa439aeffbd9f149a2b7aedac92af0feaec3b92a96ebfdaab525a8acf7b8e24b839a9aa2d14b8af187bbf95da8ec84d5c25b92b2ee9e"
            }))() # the check token is recently (by 9.20) required
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