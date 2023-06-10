# -*- coding: utf-8 -*-
"""视频 - Video - 有关 APIs"""
from . import WeapiCryptoRequest


@WeapiCryptoRequest
def GetMVDetail(mv_id: str):
    """网页端 - 获取 MV 详情

    Args:
        mv_id (str): MV ID

    Returns:
        dict
    """
    return "/weapi/v1/mv/detail", {"id": str(mv_id)}


@WeapiCryptoRequest
def GetMVResource(mv_id: str, res=1080):
    """网页端 - 获取 MV 音视频资源

    Args:
        mv_id (str): MV ID
        res (int, optional): 240 / 480 / 720 / 1080. Defaults to 1080.

    Returns:
        dict
    """
    return "/weapi/song/enhance/play/mv/url", {"id": str(mv_id), "r": str(res)}


@WeapiCryptoRequest
def GetMVComments(mv_id: str, offset=0, limit=20, total=False):
    """网页端 - 获取MV评论

    Args:
        mv_id (str): MV ID
        offset (int, optional): 时间顺序偏移数. Defaults to 0.
        limit (int, optional): 单次评论获取量. Defaults to 20.
        beforeTime (int, optional): 评论将从该时间戳（秒为单位）开始. Defaults to 0.

    Returns:
        dict
    """
    return "/weapi/v1/resource/comments/R_MV_5_%s" % mv_id, {
        "rid": "R_MV_5_%s" % mv_id,
        "offset": str(offset),
        "total": str(total).lower(),
        "limit": str(limit),
    }
