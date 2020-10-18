'''登录、Anti - AntiCSRF 有关 APIs'''
from . import EapiCryptoRequest, WeapiCryptoRequest,GetCurrentSession,logger,Crypto,LoginFailedException
import time

def WriteLoginInfo(response):
    '''写登录态入当前 Session

    Args:
        response (dict): 解码后的登录态

    Raises:
        LoginFailedException: 登陆失败时发生
    '''
    sess = GetCurrentSession()
    sess.login_info = {'tick': time.time(), 'content':response}
    if not sess.login_info['content']['code'] == 200:
        sess.login_info['success'] = False
        raise LoginFailedException(sess.login_info['content'])
    sess.login_info['success'] = True
    cookie = sess.cookies.get_dict()
    sess.csrf_token = cookie['__csrf']
    logger.debug('Updated login info for user %s' % sess.login_info['content']['profile']['nickname'])

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

@WeapiCryptoRequest
def LoginQrcodeUnikey(type=1):
    '''网页端 - 获取二维码登录令牌

    - 该令牌UUID适用于以下 URL：
     - music.163.com/login?codekey={UUID}
    - 若需要使用该URL，应由网易云音乐移动客户端扫描其二维码 - 链接不会触发入口
    - 登录态将在 `LoginQrcodeCheck` 中更新，需周期性检测
    
    Args:
        type (int, optional): 未知. Defaults to 1.

    Returns:
        dict
    '''
    return '/weapi/login/qrcode/unikey',{"type":str(type)}

@WeapiCryptoRequest
def LoginQrcodeCheck(unikey,type=1):
    '''网页端 - 二维码登录状态检测

    Args:
        key (str): 二维码 unikey
        type (int, optional): 未知. Defaults to 1.

    Returns:
        dict
    '''
    return '/weapi/login/qrcode/client/login',{'key':str(unikey),'type':type}

@WeapiCryptoRequest
def LoginTypeSwitch():
    '''网页端 - 切换登录方式 - reserved

    Returns:
        dict
    '''
    return '/weapi/w/user/login/type/switch',{}

@WeapiCryptoRequest
def GetCurrentLoginStatus():
    '''网页端 - 获取当前登录态
    
    Returns:
        dict
    '''
    return '/weapi/w/nuser/account/get',{}

def LoginViaCellphone(phone='', password='',countrycode=86,remeberLogin=True) -> dict:
    '''网页端 - 手机号登陆

    Args:
        phone (str, optional): 手机号. Defaults to ''.
        password (str, optional): 明文密码. Defaults to ''.
        countrycode (int, optional): 国家代码. Defaults to 86.
        remeberLogin (bool, optional): 是否‘自动登录’，开启可延长 CSRF 令牌时效. Defaults to True.

    Raises:
        LoginFailedException: 登陆失败时发生

    Returns:
        dict
    '''
    path='/weapi/w/login/cellphone'
    sess = GetCurrentSession()
    if (phone and password):
        sess.phone = phone
        sess.password = password
        return LoginViaCellphone()
    else:
        if (hasattr(sess,'phone') and hasattr(sess,'password')):
            md5_password = Crypto.HashHexDigest(sess.password)
            login_status = WeapiCryptoRequest(lambda:(path,{
                "phone":str(sess.phone),
                "checkToken":Crypto.checkToken(), # XXX
                "password":str(md5_password),
                "rememberLogin":str(remeberLogin).lower(),
                "countrycode":str(countrycode),
            }))() 
            WriteLoginInfo(login_status)
            return sess.login_info
        else:
            raise LoginFailedException('Not enough login info provided')

@EapiCryptoRequest
def CheckIsCellphoneRegistered(cell : str,prefix=86):
    '''移动端 - 检查某手机号是否已注册

    Args:
        cell (str): 手机号
        prefix (int): 区号 . Defaults to 86

    Returns:
        dict
    '''
    return '/eapi/cellphone/existence/check',{'cellphone':cell,'countrycode':prefix}