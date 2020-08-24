from . import WeapiCryptoRequest,GetCurrentSession,logger,Crypto,LoginFailedException
import time
def CellphoneLogin(phone='', password='',remeberLogin=True) -> dict:
    '''
        If given both phone number and password,updates them,and updates the cookies and the CSRF token

        Otherwise,if phone number and password are set,updates the cookies and the CSRF token

        Returns None if the response is invalid or the username & password combo is invalid

        Returns login info with structure tick/success/content that suggests the time/result/content of the attempt

        The value will be also set into the global variable to serve other functions
    '''
    sess = GetCurrentSession()
    if (phone and password):
        sess.phone = phone
        sess.password = password
        CellphoneLogin()
    else:
        if (sess.phone and sess.password):
            md5_password = Crypto.HashDigest(sess.password)
            r = WeapiCryptoRequest(lambda:('/weapi/login/cellphone',{"phone":str(sess.phone),"password":str(md5_password),"rememberLogin":str(remeberLogin).lower(),"checkToken":""}))()
            sess.login_info = {'tick': time.time(), 'content':r}
    
            if not sess.login_info['content']['code'] == 200:
                sess.login_info['success'] = False
                raise LoginFailedException(sess.login_info['content'])
            # HTTP Response code will always be 200.The REAL response code lies in the JSON.
            # 200 means login successful
            # 415 means the IP was reqeusting too frequently.This can be solved with a delayed request
            # 502 means the combo provided is wrong
            sess.login_info['success'] = True
            cookie = sess.cookies.get_dict()
            sess.csrf_token = cookie['__csrf']
            logger.debug('Updated login info for user %s' % sess.login_info['content']['profile']['nickname'])
            return sess.login_info
        else:
            raise LoginFailedException('Not enough login info provided')