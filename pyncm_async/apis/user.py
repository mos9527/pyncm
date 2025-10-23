# -*- coding: utf-8 -*-
"""用户 - User APIs"""
from . import WeapiCryptoRequest
import json
from typing import Union


@WeapiCryptoRequest
def GetUserDetail(user_id: Union[str, int]=0):
    """网页端 - 获取某用户资料详情

    Args:
        user_id (str, int): 用户 ID. defaults to 0

    Returns:
        dict
    """
    return f"/weapi/v1/user/detail/{user_id}", {}


@WeapiCryptoRequest
def GetUserPlaylists(user_id: Union[str, int], offset=0, limit=1001):
    """网页端 - 获取某用户创建的歌单

    Args:
        user_id (str, int): 用户 ID. defaults to 0
        offset (str, int, optional): 获取偏移数. Defaults to 0.
        limit (str, int, optional): 单次获取量. Defaults to 30.

    Returns:
        dict
    """
    return "/weapi/user/playlist", {
        "offset": str(offset),
        "limit": str(limit),
        "uid": str(user_id),
    }


@WeapiCryptoRequest
def GetUserAlbumSubs(limit: Union[str, int]=30):
    """网页端 - 获取收藏专辑内容
    Args:
        limit (str, int, optional): 单次获取量. Defaults to 30.

    Returns:
        dict
    """
    return "/weapi/album/sublist", {"limit": str(limit)}


@WeapiCryptoRequest
def GetUserArtistSubs(limit: Union[str, int]=30):
    """网页端 - 获取收藏歌手内容
    Args:
        limit (str, int, optional): 单次获取量. Defaults to 30.

    Returns:
        dict
    """
    return "/weapi/artist/sublist", {"limit": str(limit)}


SIGNIN_TYPE_MOBILE = 0
"""移动端签到 +4 EXP"""
SIGNIN_TYPE_WEB = 1
"""网页端签到 +1 EXP"""


@WeapiCryptoRequest
def SetSignin(dtype: Union[str, int]=0):
    """移动端、PC端 - 每日签到

    Args:
        dtype (str, int, optional): 签到类型，(user.SIGNIN_TYPE_MOBILE/user.SIGNIN_TYPE_WEB). Defaults to SIGNIN_TYPE_MOBILE

    Returns:
        dict
    """
    return "/weapi/point/dailyTask", {"type": str(dtype)}


@WeapiCryptoRequest
def SetWeblog(logs: dict):
    """网页端 - 用户足迹

    网易云跟踪用户行为 API，可记录内容繁多。这里暂不描述

    Args:
        logs (dict): 操作记录
    """
    return "/weapi/feedback/weblog", {"logs": json.dumps(logs, separators=(',', ':'))}
