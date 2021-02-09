'''歌曲 - Track APIs'''
from . import EapiCryptoRequest, EapiEncipered, WeapiCryptoRequest,LoginRequiredApi
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

@EapiCryptoRequest
def GetTrackAudio(song_ids:list,bitrate=320000):
    '''PC 端 - 获取歌曲音频详情（文件URL、MD5...）

    Args:
        song_ids (list): 歌曲 ID        
        bitrate (int, optional): 比特率 (96k SQ 320k HQ 320k+ Lossless/SQ). Defaults to 320000 
    Returns:
        dict
    '''

    ids = song_ids if isinstance(song_ids,list) else [song_ids]
    return '/eapi/song/enhance/player/url',{"ids":ids,"encodeType":'aac',"br":str(bitrate)}


@WeapiCryptoRequest
def GetTrackLyrics(song_id : str,lv=-1,tv=-1,rv=-1):
    '''网页端 - 获取歌曲歌词

    Args:
        song_id (str): 歌曲 ID
        lv (int, optional): 歌词版本. Defaults to -1.
        tv (int, optional): 翻译版本. Defaults to -1.
        rv (int, optional): 罗马音版本. Defaults to -1.

    `版本` 参数为 `-1` 时均会回退至最新版本

    Returns:
        dict
    '''
    return '/weapi/song/lyric',{"id": str(song_id), "lv": str(lv),"tv":str(tv),"rv":str(rv)}


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


@EapiEncipered
@WeapiCryptoRequest
@LoginRequiredApi
def SetLikeTrack(trackId,like=True,userid=0,e_r=True):
    '''PC端 - 收藏歌曲到 `我喜欢的音乐`
    
    Args:
        trackId (int): 歌曲 ID
        like (bool, optional): 收藏或取消收藏. Defaults to True.
        userid (int, optional): 暂存. Defaults to 0.

    Returns:
        dict
    '''
    return '/api/song/like',{"trackId":str(trackId),"userid":str(userid),"like":str(like).lower(),"e_r":str(e_r).lower()}    