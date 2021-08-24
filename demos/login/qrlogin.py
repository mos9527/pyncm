'''二维码登录 Demo

- 额外依赖
 - qrcode
 - Pillow
'''

from io import BytesIO
from logging import debug
from pyncm import GetCurrentSession,logger
from pyncm.apis.login import GetCurrentLoginStatus, WriteLoginInfo,LoginQrcodeUnikey,LoginQrcodeCheck
from PIL import Image
import qrcode,time,base64
# region boring GUI stuff
def dot_thingy():    
    while True:
        yield '...'
        yield '.. '
        yield '.  '
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
    return True
if __name__ == '__main__':
    print('[-] Testing login')
    print('[-] Success:',login())    