from pyncm.apis.login import LoginViaCellphone
from __init__ import assert_dep


def login():
    import inquirer

    query = inquirer.prompt(
        [
            inquirer.Text("phone", message="手机号"),
            inquirer.Password("password", message="密码"),
            inquirer.Text("ctcode", message="国家代码(默认86)"),
        ]
    )
    return LoginViaCellphone(
        query["phone"], query["password"], ctcode=query["ctcode"] or 86
    )


if __name__ == "__main__":
    print("登录测试")
    assert login(), "登陆失败"
