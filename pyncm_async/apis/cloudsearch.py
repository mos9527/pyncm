# -*- coding: utf-8 -*-
"""网易云搜索 - Cloudsearch APIs"""
from . import EapiCryptoRequest

SONG = 1
"""歌曲"""
ALBUM = 10
"""专辑"""
ARTIST = 100
"""艺术家"""
PLAYLIST = 1000
"""歌单®"""
USER = 1002
"""用户"""
MV = 1004
"""MV"""
LYRICS = 1006
"""歌词"""
DJ = 1009
"""电台"""
VIDEO = 1014
"""视频"""


@EapiCryptoRequest
def GetSearchResult(keyword: str, stype=SONG, limit=30, offset=0):
    """网页端 - 搜索某类型关键字

    Args:
        keyword (str): 搜索关键字
        type ([int, optional): 搜索类型 (cloudsearch.SONG/...). Defaults to SONG
        limit (int, optional): 单次获取量. Defaults to 30.
        offset (int, optional): 获取偏移数. Defaults to 0.

    Returns:
        dict
    """
    return "/eapi/cloudsearch/pc", {
        "s": str(keyword),
        "type": str(stype),
        "limit": str(limit),
        "offset": str(offset),
    }