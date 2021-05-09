import getpass
from pyncm import GetCurrentSession,logger,apis
def login():
    phone = input('Phone >>>')
    passw = getpass.getpass('Password >')
    apis.login.LoginViaCellphone(phone,passw)
    logger.debug(' '.join(('[+]',GetCurrentSession().login_info['content']['profile']['nickname'],'has logged in')))
    return True
if __name__ == '__main__':
    print('[-] Testing login')
    print('[-] Success:',login())