# -*- coding: utf-8 -*-
"""歌曲 - Track APIs"""
from . import EapiCryptoRequest, EapiEncipered, WeapiCryptoRequest
from ..utils import RandomString
from typing import Union
import json


@WeapiCryptoRequest
def GetTrackDetail(song_ids: Union[list, str, int]):
    """网页端 - 获取歌曲详情

    Args:
        song_ids (list, str, int): 歌曲 ID

    Notes:
        song_ids 项目数应 <= 1000

    Returns:
        dict
    """
    ids = song_ids if isinstance(song_ids, list) else [song_ids]
    return "/weapi/v3/song/detail", {"c": json.dumps([{"id": str(id)} for id in ids], separators=(',', ':'))}


@EapiCryptoRequest
def GetTrackAudio(song_ids: Union[list, str, int], bitrate=320000, encodeType="aac"):
    """PC 端 - 获取歌曲音频详情（文件URL、MD5...）

    Args:
        song_ids (list, str, int): 歌曲 ID
        bitrate (str, int, optional): 比特率 (96k SQ 320k HQ 320k+ Lossless/SQ). Defaults to 320000
        encodeType (str, optional) Defaults to `aac`. 使用高 bitrate 值时无视该选项

    Notes:
        song_ids 项目数应 <= 1000

    Returns:
        dict
    """

    ids = song_ids if isinstance(song_ids, list) else [song_ids]
    return "/eapi/song/enhance/player/url", {
        "ids": ids,
        "encodeType": str(encodeType),
        "br": str(bitrate),
    }


@EapiCryptoRequest
def GetTrackAudioV1(song_ids: Union[list, str, int], level="standard", encodeType="flac"):
    """PC 端 - 获取歌曲音频详情（文件URL、MD5...） V1

    Args:
        song_ids (list, str, int): 歌曲 ID
        level (str, optional): 音质 standard / exhigh / lossless / hires / jyeffect / sky / jymaster
        encodeType (str, optional) Defaults to `flac`. 使用高 level 值时无视该选项

    Notes:
        song_ids 项目数应 <= 1000

    Returns:
        dict
    """

    ids = song_ids if isinstance(song_ids, list) else [song_ids]
    return "/eapi/song/enhance/player/url/v1", {
        "ids": ids,
        "encodeType": str(encodeType),
        "level": str(level),
    }


@EapiCryptoRequest
def GetTrackDownloadURL(song_ids: Union[list, str, int], bitrate=320000, encodeType="aac"):
    """PC 端 - 获取资源URL

    Args:
        song_ids (list, str, int): 歌曲 ID
        bitrate (str, int, optional): 比特率 (96k SQ 320k HQ 320k+ Lossless/SQ). Defaults to 320000
        encodeType (str, optional) Defaults to `aac`. 使用高 bitrate 值时无视该选项

    Notes:
        song_ids 项目数应 <= 1000

    Returns:
        dict
    """

    # ids = song_ids if isinstance(song_ids, list) else [song_ids]
    # return "/eapi/song/enhance/download/url", {
    #     "ids": ids,
    #     "encodeType": "aac",
    #     "br": str(bitrate),
    # }

    # PC 端仅能抓取到 V1 接口，无法修复该接口，弃用。
    raise NotImplementedError("This API has been deprecated due to being non-functional.")


@EapiCryptoRequest
def GetTrackDownloadURLV1(song_ids: Union[list, str, int], level="standard"):
    """PC 端 - 获取资源URL V1

    Args:
        song_ids (list, str, int): 歌曲 ID
        level (str, optional): 音质 standard / exhigh / lossless / hires / jyeffect / sky / jymaster
    Notes:
        song_ids 项目数应 <= 1000

    Returns:
        dict
    """

    return "/eapi/song/enhance/download/url/v1", {
        "id": f"{song_ids}_0",
        "level": str(level),
    }


@WeapiCryptoRequest
def GetTrackLyrics(song_id: Union[str, int], lv=-1, tv=-1, rv=-1):
    """网页端 - 获取歌曲歌词

    Args:
        song_id (str, int): 歌曲 ID
        lv (str, int, optional): 歌词版本. Defaults to -1.
        tv (str, int, optional): 翻译版本. Defaults to -1.
        rv (str, int, optional): 罗马音版本. Defaults to -1.

    `版本` 参数为 `-1` 时均会回退至最新版本

    Returns:
        dict
    """
    return "/weapi/song/lyric", {
        "id": str(song_id),
        "lv": str(lv),
        "tv": str(tv),
        "rv": str(rv),
    }


@EapiCryptoRequest
def GetTrackLyricsV1(song_id: Union[str, int]):
    """PC 端 - 获取歌曲歌词 (新 API)

    Args:
        song_id (str, int): 歌曲 ID

    Returns:
        dict
    """
    return "/eapi/song/lyric/v1", {
        "id": str(song_id),
        "cp": False,
        "lv": 0,
        "tv": 0,
        "rv": 0,
        "kv": 0,
        "yv": 0,
        "ytv": 0,
        "yrv": 0,
    }


@WeapiCryptoRequest
def GetTrackComments(song_id: Union[str, int], offset=0, limit=20, beforeTime=0):
    """网页端 - 获取歌曲评论

    Args:
        album_id (str, int): 歌曲ID
        offset (str, int, optional): 时间顺序偏移数. Defaults to 0.
        limit (str, int, optional): 单次评论获取量. Defaults to 20.
        beforeTime (str, intv, optional): 评论将从该时间戳（秒为单位）开始. Defaults to 0.

    Returns:
        dict
    """
    return f"/weapi/v1/resource/comments/R_SO_4_{song_id}", {
        "rid": str(song_id),
        "offset": str(offset),
        "total": "true",
        "limit": str(limit),
        "beforeTime": str(beforeTime * 1000),
    }


@EapiEncipered
@EapiCryptoRequest
def SetLikeTrack(song_id: Union[str, int], like: bool=True, userid: Union[str, int]=0, e_r=True):
    """PC端 - 收藏歌曲到 `我喜欢的音乐`

    Args:
        song_id (str, int): 歌曲 ID
        like (bool, optional): 收藏或取消收藏. Defaults to True.
        userid (str, int, optional): 暂存. Defaults to 0.

    Returns:
        dict
    """
    return "/eapi/song/like", {
        "trackId": str(song_id),
        "userid": str(userid),
        "like": str(like).lower(),
        "e_r": str(e_r).lower(),
    }


DEFAULT_AUDIO_MATCHER_SESSION_ID = RandomString(16)


@WeapiCryptoRequest
def GetMatchTrackByFP(
    audioFP: str, duration: float, sessionId=DEFAULT_AUDIO_MATCHER_SESSION_ID
):
    """移动端（Chrome 插件） - 听歌识曲

    Args:
        audioFP (str): Base64 编码的 AFP. 可参考 https://github.com/mos9527/ncm-afp
        duration (float): FP 时长
        sessionId (str, optional): 未知作用. Defaults to DEFAULT_AUDIO_MATCHER_SESSION_ID.
    """
    return "/weapi/music/audio/match", {
        "algorithmCode": "shazam_v2",  # 貌似有三种？
        "sessionId": sessionId,
        "duration": float(duration),
        "from": "recognize-song",
        "times": "1",
        "decrypt": "1",
        "rawdata": audioFP,
    }
