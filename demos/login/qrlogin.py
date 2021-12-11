'''二维码登录 Demo

- 额外依赖
 - qrcode
 - Pillow
'''
import sys
sys.path.insert(0,'\\'.join(sys.path[0].split('\\')[:-2]))

import pyncm.apis
from pyncm import GetCurrentSession,logger,__version__
from pyncm.apis.login import GetCurrentLoginStatus, WriteLoginInfo,LoginQrcodeUnikey,LoginQrcodeCheck
import qrcode,time
print(__version__)
def dot_thingy():    
    while True:
        yield '...';yield '.. ';yield '.  '
dot = dot_thingy()
def login():    
    uuid = LoginQrcodeUnikey()['unikey']
    url = f'https://music.163.com/login?codekey={uuid}'
    img = qrcode.make(url)
    print('Enter 以显示二维码')
    img.show()
    logger.debug(' '.join(('[-] UUID:',uuid)))
    while True:
        rsp = LoginQrcodeCheck(uuid)
        if rsp['code'] == 803 or rsp['code'] == 800:break
        message = f"[!] {rsp['code']} -- {rsp['message']}"
        print(message,next(dot),end='\r')
        time.sleep(1)
    WriteLoginInfo(GetCurrentLoginStatus())
    logger.debug(' '.join(('[+] Logged in as %s (Last known IP: %s)' % (
            GetCurrentSession().login_info['content']['profile']['nickname'],
            GetCurrentSession().login_info['content']['profile']['lastLoginIP']
        )
    )))
    # testing search
    print('测试搜索 : hi')
    print(pyncm.apis.cloudsearch.GetSearchResult('hi'))
    return True
if __name__ == '__main__':
    print('[-] Testing login')
    print('[-] Success:',login())    