from __init__ import assert_dep

assert_dep("qrcode")
import time

import qrcode


def login():
    from pyncm import DumpSessionAsString, GetCurrentSession
    from pyncm.apis.login import (
        GetCurrentLoginStatus,
        LoginQrcodeCheck,
        LoginQrcodeUnikey,
        WriteLoginInfo,
    )

    uuid = LoginQrcodeUnikey()["unikey"]  # 获取 UUID
    print("UUID", uuid)

    url = f"https://music.163.com/login?codekey={uuid}"  # 二维码内容即这样的 URL
    img = qrcode.make(url)
    input("按 Enter 以显示二维码,扫描完毕请关闭")
    img.show()
    while True:
        for dot in ["...", ".. ", ".  "]:
            rsp = LoginQrcodeCheck(uuid)  # 检测扫描状态
            print(f"{rsp['code']} -- {rsp['message']}", dot, end="\r")
            if rsp["code"] == 803 or rsp["code"] == 800:
                # 登录成功
                print(f"{rsp['code']} -- {rsp['message']}", "...")
                WriteLoginInfo(GetCurrentLoginStatus())
                print("[!] 登录态 Session:", DumpSessionAsString(GetCurrentSession()))
                print(
                    '[-] 此后可通过 SetCurrentSession(LoadSessionFromString("PYNCMe...")) 恢复当前登录态'
                )
                return True
            time.sleep(1)


if __name__ == "__main__":
    print("二维码登录测试")
    assert login(), "登陆失败"
