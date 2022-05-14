# -*- coding: utf-8 -*-
"""私享云FM - Cloud FM APIs

`zone`即分区，已知的分区有
- `CLASSICAL` 古典
"""

from .. import EapiCryptoRequest


@EapiCryptoRequest
def GetFmZoneInfo(limit=3, zone="CLASSICAL", e_r=True):
    """获取电台内容

    Args:
        limit (int, optional): 获取数目. Defaults to 3.
        zone (str, optional): 分区. Defaults to "CLASSICAL".
        e_r (bool, optional): [未知]. Defaults to True.

    Returns:
        dict
    """
    return "/eapi/zone/fm/get", {
        "limit": str(limit),
        "zone": zone,
        "e_r": str(e_r).lower(),
    }


@EapiCryptoRequest
def SetSkipFmTrack(songId, zone="CLASSICAL", e_r=True):
    """跳过电台歌曲

    Args:
        songId (int): 歌曲ID
        zone (str, optional): 分区. Defaults to "CLASSICAL".
        e_r (bool, optional): [未知]. Defaults to True.

    Returns:
        dict
    """
    return "/eapi/zone/fm/skip", {
        "songId": str(songId),
        "zone": zone,
        "e_r": str(e_r).lower(),
        "alg": "CLSalternate",
        "time": "0",
    }
