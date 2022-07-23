from pyncm.apis.login import LoginViaCellphone,SetSendRegisterVerifcationCodeViaCellphone,GetRegisterVerifcationStatusViaCellphone
from pyncm import GetCurrentSession,DumpSessionAsString, LoadSessionFromString, SetCurrentSession
from pprint import pprint

def login():
    import inquirer
    query = inquirer.prompt(
        [
            inquirer.Text("phone", message="手机号"),            
            inquirer.Text("ctcode", message="国家代码(默认86)"),
        ]
    )
    phone,ctcode = query["phone"], query["ctcode"] or 86
    if inquirer.confirm('使用手机验证码登陆？'):
        result = SetSendRegisterVerifcationCodeViaCellphone(phone,ctcode)        
        if not result.get('code',0) == 200:
            pprint(result)
        else:
            print('[-] 已发送验证码')    
        while True:
            captcha = inquirer.text("输入验证码")
            verified = GetRegisterVerifcationStatusViaCellphone(phone,captcha,ctcode)
            pprint(verified)
            if verified.get('code',0) == 200:
                print('[-] 验证成功')
                break
        result = LoginViaCellphone(phone,captcha=captcha,ctcode=ctcode)
        pprint(result)
    else:
        password = inquirer.password("输入密码")
        result = LoginViaCellphone(phone,password=password,ctcode=ctcode)
        pprint(result)
    print('[!] 登录态 Session:',DumpSessionAsString(GetCurrentSession()))
    print('[-] 此后可通过 SetCurrentSession(LoadSessionFromString("PYNCMe...")) 恢复当前登录态')
    return True

if __name__ == "__main__":
    print("[-] 登录测试")
    assert login(), "登陆失败"
