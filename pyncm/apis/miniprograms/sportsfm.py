# -*- coding: utf-8 -*-
"""Sports FM - 跑步FM APIs"""
from .. import EapiCryptoRequest
import json


@EapiCryptoRequest
def GetSportsFMRecommendations(limit=3, bpm: int = 50, e_r=True):
    """移动端 - 小程序 - 获取跑步FM歌曲推荐

    Args:
        limit (int, optional): 获取数目. Defaults to 3.
        bpm (int): 实为‘每分钟步数’. Defaults to 50.
        e_r (bool, optional): 未知. Defaults to True.

    Returns:
        dict
    """
    return "/eapi/radio/sport/get", {
        "limit": str(limit),
        "bpm": str(bpm),
        "e_r": str(e_r).lower(),
    }


@EapiCryptoRequest
def GetCalculatedSportsFMStatus(
    distance=0, maxbpm=0, time=0, songList=[], steps=0, bpm=0, e_r=True
):
    """移动端 - 小程序 - 计算运动详情

    Args:
        distance (int, optional): 距离 - 单位未知. Defaults to 0.
        maxbpm (int, optional): 最大心率 - 暂存. Defaults to 0.
        time (int, optional): 运动用时 - 秒为单位. Defaults to 0.
        songList (list, optional): 播放过的歌曲列表. Defaults to [].
        steps (int, optional): 行进的步数. Defaults to 0.
        bpm (int, optional): 结束时刻心率. Defaults to 0.
        e_r (bool, optional): 未知. Defaults to True.

    Returns:
        dict
    """
    return "/eapi/radio/sport/calculate", {
        "distance": str(distance),
        "maxbpm": str(maxbpm),
        "time": str(time),
        "songList": json.dumps(songList),
        "steps": str(steps),
        "bpm": str(bpm),
        "e_r": str(e_r).lower(),
    }
