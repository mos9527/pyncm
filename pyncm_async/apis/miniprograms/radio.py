# -*- coding: utf-8 -*-
"""私人FM - Raido APIs"""

from .. import EapiCryptoRequest


@EapiCryptoRequest
def GetMoreRaidoContent(limit=3, e_r=True):
    """PC 端 - 拉取更多FM内容

    Args:
        limit (int, optional): 获取数目. Defaults to 3.
        e_r (bool, optional): 暂存. Defaults to True.

    Returns:
        dict
    """
    return "/api/v1/radio/get", {"limit": str(limit), "e_r": str(e_r).lower()}


@EapiCryptoRequest
def SetSkipRadioContent(songId, time=0, alg="itembased", e_r=True):
    """PC 端 - 跳过 FM 歌曲

    Args:
        songId (str): 歌曲ID
        time (int, optional): 播放时长. Defaults to 0.
        alg (str, optional): 暂存. Defaults to "itembased".
        e_r (bool, optional): 暂存. Defaults to True.

    Returns:
        dict
    """
    return "/api/v1/radio/get", {
        "e_r": str(e_r).lower(),
        "songId": str(songId),
        "alg": str(alg),
        "time": str(time),
    }


@EapiCryptoRequest
def SetLikeRadioContent(trackId, like=True, time="0", alg="itembased", e_r=True):
    """PC 端 - `收藏喜欢` FM 歌曲

    Args:
        trackId (str): 歌曲ID
        like (bool)：是否收藏
        time (int, optional): 播放时长. Defaults to 0.
        alg (str, optional): 暂存. Defaults to "itembased".
        e_r (bool, optional): 暂存. Defaults to True.

    Returns:
        dict
    """
    return "/api/v1/radio/like", {
        "e_r": str(e_r).lower(),
        "like": str(like).lower(),
        "trackId": str(trackId),
        "alg": str(alg),
        "time": str(time),
    }


@EapiCryptoRequest
def SetTrashRadioContent(songId, time="0", alg="itembased", e_r=True):
    """PC 端 - 删除 FM 歌曲

    Args:
        songId (str): 歌曲ID
        time (int, optional): 播放时长. Defaults to 0.
        alg (str, optional): 暂存. Defaults to "itembased".
        e_r (bool, optional): 暂存. Defaults to True.

    Returns:
        dict
    """
    return "/api/v1/radio/trash/add", {
        "e_r": str(e_r).lower(),
        "songId": str(songId),
        "alg": str(alg),
        "time": str(time),
    }
