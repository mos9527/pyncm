'''最嗨电音 - DI.FM APIs'''
#?WIP,I didn't really spend a lot of time looking into this,PRs are welcomed as always ;)
from . import WeapiCryptoRequest

@WeapiCryptoRequest
def GetCurrentPlayingTrackList(limit=10,source=0,channelId=101):
    '''获取当前某频道下正在播放的歌曲

    Args:
        limit (int, optional): 单次获取数量. Defaults to 10.
        source (int, optional): [未知]. Defaults to 0.
        channelId (int, optional): 频道 (channel) ID. Defaults to 101.

    Returns:
        dict
    '''
    return '/api/dj/difm/playing/tracks/list',{'limit':str(limit),'source':str(source),'channelId':str(channelId)}

@WeapiCryptoRequest
def GetChannelCollection(source=0):
    '''获取所有频道的信息

    Args:
        source (int, optional): [未知]. Defaults to 0.

    Returns:
        dict
    '''
    return '/api/dj/difm/all/style/channel/v2',{'sources':"[%s]" % source}