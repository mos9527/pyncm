# -*- coding: utf-8 -*-
"""我的音乐云盘 - Cloud APIs"""
import json
from . import WeapiCryptoRequest, EapiCryptoRequest, GetCurrentSession

BUCKET = "jd-musicrep-privatecloud-audio-public"


@WeapiCryptoRequest
def GetCloudDriveInfo(limit=30, offset=0):
    """PC端 - 获取个人云盘内容

    Args:
        limit (int, optional): 单次获取量. Defaults to 30.
        offset (int, optional): 获取偏移数. Defaults to 0.

    Returns:
        dict
    """
    return "/weapi/v1/cloud/get", {"limit": str(limit), "offset": str(offset)}


@WeapiCryptoRequest
def GetCloudDriveItemInfo(song_ids: list):
    """PC端 - 获取个人云盘项目详情

    Args:
        song_ids (list): 云盘项目 ID

    Returns:
        dict
    """
    ids = song_ids if isinstance(song_ids, list) else [song_ids]
    return "/weapi/v1/cloud/get/byids", {"songIds": ids}


@EapiCryptoRequest
def GetNosToken(
    filename,
    md5,
    fileSize,
    ext,
    ftype="audio",
    nos_product=3,
    bucket=BUCKET,
    local=False,
):
    """移动端 - 云盘占位

    Args:
        filename (str): 文件名
        md5 (str): 文件 MD5
        fileSize (str): 文件大小
        ext (str): 文件拓展名
        ftype (str, optional): 上传类型. Defaults to 'audio'.
        nos_product (int, optional): APP类型. Defaults to 3.
        bucket (str, optional): 转存bucket. Defaults to 'jd-musicrep-privatecloud-audio-public'.
        local (bool, optional): 未知. Defaults to False.

    Returns:
        dict
    """
    return "/eapi/nos/token/alloc", {
        "type": str(ftype),
        "nos_product": str(nos_product),
        "md5": str(md5),
        "local": str(local).lower(),
        "filename": str(filename),
        "fileSize": str(fileSize),
        "ext": str(ext),
        "bucket": str(bucket),
    }


async def SetUploadObject(
    stream, md5, fileSize, objectKey, token, offset=0, compete=True, bucket=BUCKET, session=None
):
    """移动端 - 上传内容

    Args:
        stream : bytes / File 等数据体 .e.g open('file.mp3')
        md5 : 数据体哈希
        objectKey : GetNosToken 获得
        token : GetNosToken 获得
        offset (int, optional): 续传起点. Defaults to 0.
        compete (bool, optional): 文件是否被全部上传. Defaults to True.

    Returns:
        dict
    """
    r = await (session or GetCurrentSession()).post(
        "http://45.127.129.8/%s/" % bucket + objectKey.replace("/", "%2F"),
        data=stream,
        params={"version": "1.0", "offset": offset, "complete": str(compete).lower()},
        headers={
            "x-nos-token": token,
            "Content-MD5": md5,
            "Content-Type": "cloudmusic",
            "Content-Length": str(fileSize),
        },
    )
    return json.loads(r.text)


@EapiCryptoRequest
def GetCheckCloudUpload(md5, ext="", length=0, bitrate=0, songId=0, version=1):
    """移动端 - 检查云盘资源

    Args:
        md5 (str): 资源MD5哈希
        ext (str, optional): 文件拓展名. Defaults to ''.
        length (int, optional): 文件大小. Defaults to 0.
        bitrate (int, optional): 音频 - 比特率. Defaults to 0.
        songId (int, optional): 云盘资源ID. Defaults to 0 表示新资源.
        version (int, optional): 上传版本. Defaults to 1.

    Returns:
        dict
    """
    return "/eapi/cloud/upload/check", {
        "songId": str(songId),
        "version": str(version),
        "md5": str(md5),
        "length": str(length),
        "ext": str(ext),
        "bitrate": str(bitrate),
    }


@EapiCryptoRequest
def SetUploadCloudInfo(
    resourceId, songid, md5, filename, song=".", artist=".", album=".", bitrate=128
):
    """移动端 - 云盘资源提交

    注：
        - MD5 对应文件需已被 SetUploadObject 上传
        - song 项不得包含字符 .和/

    Args:
        resourceId (str): GetNosToken 获得
        songid (str): GetCheckCloudUpload 获得
        md5 (str): 文件MD5哈希
        filename (str): 文件名
        song (str, optional): 歌名 / 标题. Defaults to ''.
        artist (str, optional): 艺术家名. Defaults to ''.
        album (str, optional): 专辑名. Defaults to ''.
        bitrate (int, optional): 音频 - 比特率. Defaults to 0.

    WIP - 封面ID,歌词ID 等

    Returns:
        dict
    """
    return "/eapi/upload/cloud/info/v2", {
        "resourceId": str(resourceId),
        "songid": str(songid),
        "md5": str(md5),
        "filename": str(filename),
        "song": str(song),
        "artist": str(artist),
        "album": str(album),
        "bitrate": bitrate,
    }


@EapiCryptoRequest
def SetPublishCloudResource(songid):
    """移动端 - 云盘资源发布

    Args:
        songid (str): 来自 SetUploadCloudInfo

    Returns:
        SetUploadCloudInfo
    """
    return "/eapi/cloud/pub/v2", {
        "songid": str(songid),
    }


async def SetRectifySongId(oldSongId, newSongId,session=None):
    """移动端 - 歌曲纠偏

    Args:
        oldSongId : 欲纠偏的源歌曲ID
        newSongId : 欲纠偏的目标歌曲ID

    Returns:
        dict
    """
    resp = await (session or GetCurrentSession()).get(
            "/api/cloud/user/song/match",
            params={"songId": str(oldSongId), "adjustSongId": str(newSongId)},
    )
    return resp.json()
