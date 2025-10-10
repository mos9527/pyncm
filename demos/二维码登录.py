from __init__ import assert_dep
try:
    assert_dep("qrcode")
except AssertionError:
    print("module 'qrcode' not installed")
import time
import qrcode


def generate_chain_id() -> str:
    import random
    from pyncm import GetCurrentSession

    # 从全局的session中获取sDeviceId,不存在则生成
    s_device_id = GetCurrentSession().cookies.get("sDeviceId")
    if not s_device_id:
        random_num = random.randrange(1000000)
        s_device_id = f"unknown-{random_num}"
    timestamp = int(time.time() * 1000)
    return f"v1_{s_device_id}_web_login_{timestamp}"


def login():
    from pyncm.apis.login import (
        GetCurrentLoginStatus,
        WriteLoginInfo,
        LoginQrcodeUnikey,
        LoginQrcodeCheck,
    )
    from pyncm import GetCurrentSession, DumpSessionAsString

    uuid = LoginQrcodeUnikey()["unikey"]  # 获取 UUID
    print("UUID", uuid)

    url = f"http://music.163.com/login?codekey={uuid}&chainId={generate_chain_id()}"  # 二维码内容即这样的 URL
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
                WriteLoginInfo(GetCurrentLoginStatus(),)
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
