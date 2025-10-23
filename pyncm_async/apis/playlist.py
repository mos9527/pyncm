# -*- coding: utf-8 -*-
"""歌单 - Playlist APIs"""

import json
from typing import Union
from . import EapiCryptoRequest, WeapiCryptoRequest, GetCurrentSession


@WeapiCryptoRequest
def GetPlaylistInfo(playlist_id: Union[str, int], offset=0, total=True, limit=1000):
    """网页端 - 获取歌单内容

    Note:
        摘自：https://binaryify.github.io/NeteaseCloudMusicApi/#/?id=%e8%8e%b7%e5%8f%96%e6%ad%8c%e5%8d%95%e8%af%a6%e6%83%85
        歌单能看到歌单名字, 但看不到具体歌单内容 , 调用此接口 , 传入歌单 id, 可 以获取对应歌单内的所有的音乐
        (未登录状态只能获取不完整的歌单,登录后是完整的)，但是返回的 trackIds 是完整的，tracks 则是不完整的
        
        因此，你可以通过 GetPlaylistAllTracks 获取完整的歌单内容

    Args:
        playlist_id (str, int): 歌单 ID
        offset (str, int, optional): **无效** 获取偏移数. Defaults to 0.
        total (bool, optional): **无效** 是否获取全部内容. Defaults to True.
        limit (str, int, optional): **无效** 单次获取量. Defaults to 30.

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


async def GetPlaylistAllTracks(playlist_id: Union[str, int], offset=0, limit=1000, session=None):
    """网页端 - 获取歌单所有歌曲

    Args:
        playlist_id (str, int): 歌单 ID
        offset (str, int, optional): 获取偏移数. Defaults to 0.
        limit (str, int, optional): 单次获取量. Defaults to 1000.

    Returns:
        dict
    """
    session = session or GetCurrentSession()
    data = await GetPlaylistInfo(playlist_id, offset, True, limit, session=session)
    trackIds = [track["id"] for track in data["playlist"]["trackIds"]]
    id = trackIds[offset : offset + limit]
    from .track import GetTrackDetail

    return await GetTrackDetail(id)


@WeapiCryptoRequest
def GetPlaylistComments(playlist_id: Union[str, int], pageNo=1, pageSize=20, cursor=-1, offset=0, orderType=1):
    """网页端 - 获取歌单评论

    Args:
        playlist_id (str, int): 歌单ID
        pageNo (str, int, optional): 页数. Defaults to 1.
        pageSize (str, int, optional): 单次评论获取量. Defaults to 20.
        cursor (str, int, optional): 评论将从该时间戳（毫秒为单位）开始. Defaults to -1.
        offset (str, int, optional): 时间顺序偏移数. Defaults to 0.
        orderType (str, int, optional): **无效** 评论排序方式,. Defaults to 1.

    Returns:
        dict
    """
    return "/weapi/comment/resource/comments/get", {
        "rid": f"A_PL_0_{playlist_id}",
        "threadId": f"A_PL_0_{playlist_id}",
        "pageNo": str(pageNo),
        "pageSize": str(pageSize),
        "cursor": str(cursor),
        "offset": str(offset),
        "orderType": str(orderType),
    }


@WeapiCryptoRequest
def SetManipulatePlaylistTracks(playlist_ids: Union[list, str, int], playlistId, op="add", imme=True, e_r=True):
    """PC 端 - 操作歌单

    - op 有以下几种：
     - `add` : 添加到歌单
     - `del` : 从歌单删除

    Args:
        playlist_ids (list, str, int): 待操作的歌曲ID列表
        playlistId (str, int): 要操作的歌单ID
        op (str, optional): 操作 . Defaults to "add".
        imme (bool, optional): 暂存. Defaults to True.

    Returns:
        [type]: [description]
    """
    playlist_ids = playlist_ids if isinstance(playlist_ids, list) else [playlist_ids]
    return "/weapi/v1/playlist/manipulate/tracks", {
        "trackIds": json.dumps(playlist_ids, separators=(',', ':')),
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
def SetRemovePlaylist(playlist_ids: Union[list, int, str], self=True):
    """移动端 - 删除歌单

    Args:
        playlist_ids (list, str, int): 歌单 ID
        self (bool): 未知. Defaults to True
    Returns:
        dict
    """
    playlist_ids = playlist_ids if isinstance(playlist_ids, list) else [playlist_ids]
    return "/eapi/playlist/remove", {
        "ids": str(playlist_ids),
        "self": str(self),
    }
