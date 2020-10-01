'''二维码登录 Demo

- 额外依赖
 - qrcode
 - Pillow
'''

from pyncm.apis.login import GetCurrentLoginStatus, WriteLoginInfo
import pyncm
from PIL import ImageFont,ImageDraw
import qrcode,time

def dot_thingy():    
    while True:
        s = list('   ')
        while s.count('.') < len(s):
            s[s.count('.')] = '.'
            yield ''.join(s)
dot = dot_thingy()

uuid = pyncm.login.LoginQrcodeUnikey()['unikey']
url = f'https://music.163.com/login?codekey={uuid}'
img = qrcode.make(url) # dimesion will always be 490,490
font = ImageFont.truetype('simhei.ttf',20) # 黑体
canvas = ImageDraw.Draw(img)
canvas.text((10,10),'网易云音乐APP->侧边栏->下滑->扫描二维码√',font=font)
canvas.text((7,430),'请时刻注意终端输出，扫描完毕后可关闭本对话框',font=font)
img.show() # though tkinter was too expensive to use so here's my repalcement (((
print('[-] 二维码 UUID:',uuid)
while True:
    rsp = pyncm.login.LoginQrcodeCheck(uuid)
    if rsp['code'] == 803 or rsp['code'] == 800:break
    message = f"[!] {rsp['code']} -- {rsp['message']}"
    print(message,next(dot),end='\r')
    time.sleep(1)
WriteLoginInfo(GetCurrentLoginStatus())
print('[+] 登录成功。欢迎，%s (上一次登录 IP: %s)...尝试签到' % (
        pyncm.GetCurrentSession().login_info['content']['profile']['nickname'],
        pyncm.GetCurrentSession().login_info['content']['profile']['lastLoginIP']
    )
)

r = pyncm.user.SetSignin(pyncm.user.SIGNIN_TYPE_MOBILE)
if r['code'] == 200:
    print('[+] 签到完成 - EXP +%d' % r['point'])
else:
    print('[+] 无法签到 - %s' % r['msg'])