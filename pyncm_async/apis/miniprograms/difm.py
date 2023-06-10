# -*- coding: utf-8 -*-
"""最嗨电音、爵士电台 - DI.FM APIs"""

from .. import WeapiCryptoRequest


@WeapiCryptoRequest
def GetCurrentPlayingTrackList(channelId=101, limit=10, source=0):
    """移动端 - 小程序 - 获取当前某频道下正在播放的歌曲

    Args:
        channelId (int, optional): 频道 (channel) ID. Defaults to 101.
        limit (int, optional): 单次获取数量. Defaults to 10.
        source (int, optional): [未知]. Defaults to 0.

    Returns:
        dict
    """
    return "/api/dj/difm/playing/tracks/list", {
        "limit": str(limit),
        "source": str(source),
        "channelId": str(channelId),
    }


@WeapiCryptoRequest
def GetChannelCollection(source=0):
    """移动端 - 小程序 - 获取所有频道的信息

    Args:
        source (int, optional): [未知]. Defaults to 0.

    Returns:
        dict
    """
    return "/api/dj/difm/all/style/channel/v2", {"sources": "[%s]" % source}


@WeapiCryptoRequest
def GetChannelSubscriptionCollection(source=0):
    """移动端 - 小程序 - 获取所有*订阅*频道的信息

    Args:
        source (int, optional): [未知]. Defaults to 0.

    Returns:
        dict
    """
    return "/api/dj/difm/subscribe/channels/get/v2", {"sources": "[%s]" % source}


@WeapiCryptoRequest
def SetChannelSubcribiton(id, set_subsubscribe=True):
    """移动端 - 小程序 - 收藏电台

    Args:
        id (str): 电台ID
        set_subsubscribe (bool, optional): 订阅或取消订阅. Defaults to True

    Returns:
        dict
    """
    return (
        "/api/dj/difm/channel/subscribe"
        if set_subsubscribe
        else "/api/dj/difm/channel/unsubscribe",
        {"id": str(id)},
    )
