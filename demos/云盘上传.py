import hashlib, os
from __init__ import login

def md5sum(file):
    md5sum = hashlib.md5()
    with open(file, "rb") as f:
        while chunk := f.read():
            md5sum.update(chunk)
    return md5sum


def upload_one(path):
    from pyncm import GetCurrentSession
    from pyncm.apis.cloud import (
        GetCheckCloudUpload,
        GetNosToken,
        SetUploadObject,
        SetUploadCloudInfo,
        SetPublishCloudResource,
    )

    fname = os.path.basename(path)
    fext = path.split(".")[-1]
    """Parsing file names"""
    fsize = os.stat(path).st_size
    md5 = md5sum(path).hexdigest()
    print("MD5", md5)
    cresult = GetCheckCloudUpload(md5)
    songId = cresult["songId"]
    """网盘资源发布 4 步走：
    1.拿到上传令牌 - 需要文件名，MD5，文件大小"""
    token = GetNosToken(fname, md5, fsize, fext)["result"]
    if cresult["needUpload"]:
        print("开始上传 %s ( %s B )" % (fname, fsize))
        """2. 若文件未曾上传完毕，则完成其上传"""
        upload_result = SetUploadObject(
            open(path, "rb"), md5, fsize, token["objectKey"], token["token"]
        )
        print("响应", upload_result)
    print(
        f"""准备提交
    ID  :   {songId}
    MD5 :   {md5}
    NAME:   {fname}"""
    )
    submit_result = SetUploadCloudInfo(
        resourceId=token["resourceId"],
        songid=songId,
        md5=md5,
        filename=fname,
        song=fname,
        artist=GetCurrentSession().nickname,
        album="PyNCM",
        bitrate=1000,
    )
    """3. 提交资源"""
    print("提交响应", submit_result)
    """4. 发布资源"""
    publish_result = SetPublishCloudResource(submit_result["songId"])
    print("发布结果", publish_result)


if __name__ == "__main__":    
    assert login(), "登录失败"
    # login via phone,may change as you like
    upload_one(input("文件路径："))
