'''二维码登录 Demo

- 额外依赖
 - qrcode
 - Pillow
'''

from io import BytesIO
from pyncm.apis.login import GetCurrentLoginStatus, WriteLoginInfo
import pyncm
from PIL import Image
import qrcode,time,base64
# region getting GUI stuff to work cross-platformly
def dot_thingy():    
    while True:
        s = list('   ')
        while s.count('.') < len(s):
            s[s.count('.')] = '.'
            yield ''.join(s)
dot = dot_thingy()
im1 = b'iVBORw0KGgoAAAANSUhEUgAAAMIAAAAJCAIAAADvrGQRAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAAEnQAABJ0Ad5mH3gAAAPPSURBVFhHrViLsdswDHtzeaDM42m8jIdJAYKkSElJ/e4erk1lSQT4k+zrz32dx8+K1/UO3Ner7igr7/f18tnEcd6+loD9OincFD8O52/UfweIHOdpnh6vyzy5z5dcus9ziG4cNVvM3ZcMGfETNy0wIbQFV8C60dzwRBk4DnfpCb56EdzchkGE8Ahpy1xckSUCkpzpzQLHbftP3RlouaV9wXOPZPg6pUw78yTNmWl7RCqvJSejpEWfLk+PM0YOA4wmIrogxNyWCEvvXOfwLhBzzrvbYlh1Az2bCTUmk4Dmhoe/Yrb+kLEDe8Jcgr1smax5mhhFSV+1zYsX63n4ErGfbQTwULwQjBzsgXfhIfkMpQxT2TNvuzzjIMCfyXsNpscVcLgomQwlGJm1kYXbJFWPuBWRBysJA8+bsuJDDrpuYg3PG0M3UQFC3hF05lKOutmzOVbpZMauPf+F7z/CEScNGLkFH6mPDXYbYRL3Fbexp3gNPhEeZwHMJTiFJ8lWBHjHRw++WSS8Qjyq6UW2iy6O6XELkEsGJIjJuBhybyOLADe+ZJJYR11IsWdI3QLPU5+/Ab5scGQ9D6jcajvQmauLQqm4B6fPFV0o5a76DK+Ivcxa4VzLJHSJulqWSC81EKgiUajIrEGrFgdTsr7EMbtPgIfiGAXrmOQAzUSuvA6APfdHj12oXpi1tY63jY3X28gzUkZjJrRwjRUZU/muW+FaNKgr8VILR1L1CbP2sPMS40iZ0/giM0LRlpC+wk4NNvMPHqsZJK036HaUwL7p2KFsI7OhBWMikZMYYA3nYYdfNVnlNnh4y7x75ePdhiCnfr1aMpNGPN0I0+MWIvaxR8Z/4++o3vAqBmONSirGU1TdQNEqUBdhMc5E6YMdktlzM8vI+2x7ztR2/E4uhC+wLm4BpMPtaRLwu76KccA4izbi951YrDw8sRG4uge/1oe+PmVlnBHtrujeTLHkdmd0GYB3BpGKv2ujqZbeHsiCffwxISFJZP7DJgKSjls/wa6HgE0bscIh8qSNFublyqt+uqBm6u9DgNy+bWYz9eXkpsT0UpswAjdLGmIg+6mIJZ6Nyuc2Cr5WUy8ceLRGa/+gSlNRNpWG0g8Oy0VQu2FIcje+ngCbVwjNntaaLtjIr7qBkc2C0auZ6k+V3jGbuVIRGD45Z/Naq0sgCSoE30LtGVEidYsm5PbaRllFwQmHjCiF5pYt9GPSe66ssXs0IOemKn8H+IBODAkIF0kv3fQ/Y0TuX/Lza2wpomlU8l9lYb85QsnFJhtyT7Ft/RlWfWq93/8AexcHtWBkZx4AAAAASUVORK5CYII='
im2 = b'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'
# don't mind these.they're base64 encoded images for prompts
im1,im2 = base64.b64decode(im1),base64.b64decode(im2)
im1,im2 = Image.open(BytesIO(im1)),Image.open(BytesIO(im2))
#endregion
uuid = pyncm.login.LoginQrcodeUnikey()['unikey']
url = f'https://music.163.com/login?codekey={uuid}'
img = qrcode.make(url) # dimesion will always be 490,490
img.paste(im1,(10,10))
img.paste(im2,(7,430))
img.show() # though tkinter was too expensive to use so here's my repalcement (((
print('[-] 二维码 UUID:',uuid)
while True:
    rsp = pyncm.login.LoginQrcodeCheck(uuid)
    if rsp['code'] == 803 or rsp['code'] == 800:break
    message = f"[!] {rsp['code']} -- {rsp['message']}"
    print(message,next(dot),end='\r')
    time.sleep(1)
WriteLoginInfo(GetCurrentLoginStatus())
print('[+] 登录成功。欢迎，%s (上一次登录 IP: %s)' % (
        pyncm.GetCurrentSession().login_info['content']['profile']['nickname'],
        pyncm.GetCurrentSession().login_info['content']['profile']['lastLoginIP']
    )
)