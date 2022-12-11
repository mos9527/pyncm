import importlib
import sys,os

IS_FIRSTTIME = sys.path[0] != '.'

def assert_dep(name):
    assert importlib.util.find_spec(name), "需要安装 %s" % name


def login():
    import inquirer
    import demos.手机登录 as 手机登录, 二维码登录
    class 匿名登陆:
        @staticmethod
        def login():
            from pyncm.apis.login import LoginViaAnonymousAccount
            return LoginViaAnonymousAccount()
    methods = {"手机登录": 手机登录, "二维码登录": 二维码登录,"匿名登陆": 匿名登陆}
    assert methods[
        inquirer.prompt([inquirer.List("method", message="登陆方法", choices=methods)])["method"]
    ].login(), "登录失败"
    from pyncm import GetCurrentSession

    print(
        "已登录",
        GetCurrentSession().nickname,
        "用户 ID：",
        GetCurrentSession().uid,
    )
    return True


assert_dep("pyncm")
assert_dep("inquirer")
# Find pyncm from working directories first,
if IS_FIRSTTIME:
    import inquirer
    if inquirer.confirm('使用调试模式'):
        os.environ['PYNCM_DEBUG'] = 'DEBUG'
    sys.path.insert(0,'.')
    from pyncm import __version__,__file__
    print("PyNCM %s" % __version__,__file__)
