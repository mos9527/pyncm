import importlib


def assert_dep(name):
    assert importlib.util.find_spec(name), "需要安装 %s" % name


def login():
    import inquirer
    import demos.手机登录 as 手机登录, 二维码登录

    methods = {"手机登录": 手机登录, "二维码登录": 二维码登录}
    assert methods[
        inquirer.prompt([inquirer.List("method", message="登陆方法", choices=methods)])[
            "method"
        ]
    ].login(), "登录失败"
    from pyncm import GetCurrentSession

    print(
        "已登录",
        GetCurrentSession().nickname,
        "曾用 IP：",
        GetCurrentSession().lastIP,
        "用户 ID：",
        GetCurrentSession().uid,
    )
    return True


assert_dep("pyncm")
assert_dep("inquirer")
from pyncm import __version__

print("PyNCM %s" % __version__)
