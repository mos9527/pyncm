# -*- coding: utf-8 -*-
"""专辑 - Album APIs"""
from . import WeapiCryptoRequest


@WeapiCryptoRequest
def GetAlbumInfo(album_id: str):
    """网页端 - 获取专辑信息

    Args:
        album_id (str): 专辑ID

    Returns:
        dict
    """
    return "/weapi/v1/album/%s" % album_id, {}


@WeapiCryptoRequest
def GetAlbumComments(album_id: str, offset=0, limit=20, beforeTime=0):
    """网页端 - 获取专辑评论

    Args:
        album_id (str): 专辑ID
        offset (int, optional): 时间顺序偏移数. Defaults to 0.
        limit (int, optional): 单次评论获取量. Defaults to 20.
        beforeTime (int, optional): 评论将从该时间戳（秒为单位）开始. Defaults to 0.

    Returns:
        dict
    """
    return "/weapi/v1/resource/comments/R_AL_3_%s" % album_id, {
        "rid": "R_AL_3_%s" % album_id,
        "offset": str(offset),
        "total": "true",
        "limit": str(limit),
        "beforeTime": str(beforeTime * 1000),
    }
