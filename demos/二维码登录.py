from __init__ import assert_dep

assert_dep("qrcode")
import time
import qrcode


def login():
    from pyncm.apis.login import (
        GetCurrentLoginStatus,
        WriteLoginInfo,
        LoginQrcodeUnikey,
        LoginQrcodeCheck,
        GetLoginQRCodeUrl
    )
    from pyncm import GetCurrentSession, DumpSessionAsString

    uuid = LoginQrcodeUnikey()["unikey"]  # 获取 UUID
    print("UUID", uuid)

    url = GetLoginQRCodeUrl(uuid) # 使用此函数来正确生成二维码链接
    img = qrcode.make(url)
    input("按 Enter 以显示二维码,扫描完毕请关闭")
    img.show()
    while True:
        for dot in ["...", ".. ", ".  "]:
            rsp = LoginQrcodeCheck(uuid)  # 检测扫描状态
            print(f"{rsp['code']} -- {rsp['message']}", dot, end="\r")
            if rsp["code"] == 803:
                # 登录成功
                print(f"{rsp['code']} -- {rsp['message']}", "...")
                WriteLoginInfo(
                    GetCurrentLoginStatus(),
                )
                print("[!] 登录态 Session:", DumpSessionAsString(GetCurrentSession()))
                print(
                    '[-] 此后可通过 SetCurrentSession(LoadSessionFromString("PYNCMe...")) 恢复当前登录态'
                )
                return True
            if rsp["code"] == 8821:
                # 登录异常风控机制
                print()
                return
            if rsp["code"] == 800:
                # 二维码过期或不存在
                print()
                return
            time.sleep(1)


if __name__ == "__main__":
    print("二维码登录测试")
    assert login(), "登陆失败"
