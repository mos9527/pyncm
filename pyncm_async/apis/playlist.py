# -*- coding: utf-8 -*-
"""歌单 - Playlist APIs"""

import json

from . import EapiCryptoRequest, WeapiCryptoRequest


@WeapiCryptoRequest
def GetPlaylistInfo(playlist_id, offset=0, total=True, limit=1000):
    """网页端 - 获取歌单内容

    Note:
        摘自：https://binaryify.github.io/NeteaseCloudMusicApi/#/?id=%e8%8e%b7%e5%8f%96%e6%ad%8c%e5%8d%95%e8%af%a6%e6%83%85
        歌单能看到歌单名字, 但看不到具体歌单内容 , 调用此接口 , 传入歌单 id, 可 以获取对应歌单内的所有的音乐
        (未登录状态只能获取不完整的歌单,登录后是完整的)，但是返回的 trackIds 是完整的，tracks 则是不完整的
        
        因此，你可以通过 GetPlaylistAllTracks 获取完整的歌单内容

    Args:
        playlist_id ([type]): 歌单 ID
        offset (int, optional): **无效** 获取偏移数. Defaults to 0.
        total (bool, optional): **无效** 是否获取全部内容. Defaults to True.
        limit (int, optional): **无效** 单次获取量. Defaults to 30.

    Returns:
        dict
    """
    return "/weapi/v6/playlist/detail", {
        "id": str(playlist_id),
        "offset": str(offset),
        "total": str(total).lower(),
        "limit": str(limit),
        "n": str(limit),
    }


async def GetPlaylistAllTracks(playlist_id, offset=0, limit=1000):
    """网页端 - 获取歌单所有歌曲

    Args:
        playlist_id ([type]): 歌单 ID
        offset (int, optional): 获取偏移数. Defaults to 0.
        limit (int, optional): 单次获取量. Defaults to 1000.

    Returns:
        dict
    """
    data = await GetPlaylistInfo(playlist_id, offset, True, limit)
    trackIds = [track["id"] for track in data["playlist"]["trackIds"]]
    id = trackIds[offset : offset + limit]
    from .track import GetTrackDetail

    return await GetTrackDetail(id)


@WeapiCryptoRequest
def GetPlaylistComments(playlist_id: str, offset=0, limit=20, beforeTime=0):
    """网页端 - 获取歌单评论

    Args:
        album_id (str): 歌单ID
        offset (int, optional): 时间顺序偏移数. Defaults to 0.
        limit (int, optional): 单次评论获取量. Defaults to 20.
        beforeTime (int, optional): 评论将从该时间戳（秒为单位）开始. Defaults to 0.

    Returns:
        dict
    """
    return "/v1/resource/comments/A_PL_0_%s" % playlist_id, {
        "rid": str(playlist_id),
        "limit": str(limit),
        "offset": str(offset),
        "beforeTime": str(beforeTime * 1000),
    }


@WeapiCryptoRequest
def SetManipulatePlaylistTracks(trackIds, playlistId, op="add", imme=True, e_r=True):
    """PC 端 - 操作歌单

    - op 有以下几种：
     - `add` : 添加到歌单
     - `del` : 从歌单删除

    Args:
        trackIds (list[str]): 待操作的歌曲ID列表
        playlistId ([int]): 要操作的歌单ID
        op (str, optional): 操作 . Defaults to "add".
        imme (bool, optional): 暂存. Defaults to True.

    Returns:
        [type]: [description]
    """
    trackIds = trackIds if isinstance(trackIds, list) else [trackIds]
    return "/weapi/v1/playlist/manipulate/tracks", {
        "trackIds": json.dumps(trackIds),
        "pid": str(playlistId),
        "op": op,
        "imme": str(imme).lower(),
    }


@EapiCryptoRequest
def SetCreatePlaylist(name: str, privacy=False):
    """PC 端 - 新建歌单

    Args:
        name (str): 歌单名
        privacy (bool, optional) : 是否私享. Defaults to False.
    """
    return "/eapi/playlist/create", {
        "name": str(name),
        "privacy": str(privacy * 1),
    }


@EapiCryptoRequest
def SetRemovePlaylist(ids: list, self=True):
    """移动端 - 删除歌单

    Args:
        ids (list): 歌单 ID
        self (bool): 未知. Defaults to True
    Returns:
        dict
    """
    ids = ids if isinstance(ids, list) else [ids]
    return "/eapi/playlist/remove", {
        "ids": str(ids),
        "self": str(self),
    }
