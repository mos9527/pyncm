'''歌曲 - Track APIs'''
from . import WeapiCryptoRequest,EapiCryptoRequest,LoginRequiredApi
from . import logger
import json
@WeapiCryptoRequest
def GetTrackDetail(song_ids : list):
    '''网页端 - 获取歌曲详情

    Args:
        song_ids (list): 歌曲 ID

    Returns:
        dict
    '''
    ids = song_ids if isinstance(song_ids,list) else [song_ids]
    return '/weapi/v3/song/detail',{"c":json.dumps([{'id': str(id)} for id in ids])}

@WeapiCryptoRequest
def GetTrackAudio(song_ids:list, quality='lossless',encodeType='aac'):
    '''网页端 - 获取歌曲音频详情（文件URL、MD5...）

    Args:
        song_ids (list): 歌曲 ID
        quality (str, optional): standard / high / lossless . Defaults to 'lossless'.
        encodeType (str, optional): 歌曲编码 . Defaults to 'aac'.

    Returns:
        dict
    '''
    if not quality in ['standard', 'higher', 'lossless']:
        logger.warn('Invalid quality config `%s`,falling back to `standard`')
        quality = 'standard'
    # Quality check
    ids = song_ids if isinstance(song_ids,list) else [song_ids]
    return '/weapi/song/enhance/player/url/v1',{"ids":ids,"level":quality,"encodeType":encodeType}


@WeapiCryptoRequest
def GetTrackLyrics(song_id : str):
    '''网页端 - 获取歌曲歌词

    Args:
        song_id (str): 歌曲ID

    Returns:
        dict
    '''
    return '/weapi/song/lyric',{"id": str(song_id), "lv": -1, "tv": -1}


@WeapiCryptoRequest
def GetTrackComments(song_id, offset=0, limit=20,beforeTime=0):
    '''网页端 - 获取歌曲评论

    Args:
        album_id (str): 歌曲ID
        offset (int, optional): 时间顺序偏移数. Defaults to 0.
        limit (int, optional): 单次评论获取量. Defaults to 20.
        beforeTime (int, optional): 评论将从该时间戳（秒为单位）开始. Defaults to 0.

    Returns:
        dict
    '''
    return '/weapi/v1/resource/comments/R_SO_4_%s' % song_id,{"rid":str(song_id),"offset":str(offset),"total":"true","limit":str(limit),"beforeTime":str(beforeTime * 1000)}


@EapiCryptoRequest
@LoginRequiredApi
def SetLikeTrack(trackId,like=True,userid=0,e_r=True):
    '''PC端 - 收藏歌曲到 `我喜欢的音乐` - WIP  - WIP - protected via 网易易盾

    TODO: defeat `watchman.js` obfuscation
    
    Args:
        trackId (int): 歌曲 ID
        like (bool, optional): 收藏或取消收藏. Defaults to True.
        userid (int, optional): 暂存. Defaults to 0.

    Returns:
        dict
    '''
    return '/api/song/like',{"trackId":str(trackId),"userid":str(userid),"like":str(like).lower(),"e_r":str(e_r).lower()}    