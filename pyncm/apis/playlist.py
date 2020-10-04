'''歌单 - Playlist APIs'''
import json
from . import LapiCryptoRequest, WeapiCryptoRequest , EapiCryptoRequest

@WeapiCryptoRequest
def GetPlaylistInfo(playlist_id,offset=0,total=True,limit=1000):
    '''网页端 - 获取歌单内容

    Args:
        playlist_id ([type]): 歌单 ID
        offset (int, optional): 获取偏移数. Defaults to 0.
        total (bool, optional): 是否获取全部内容. Defaults to True.
        limit (int, optional): 单次获取量. Defaults to 30.
    
    Returns:
        dict
    '''
    return '/weapi/v6/playlist/detail',{"id":str(playlist_id),"offset":str(offset),"total":str(total).lower(),"limit":str(limit)}

@WeapiCryptoRequest
def GetPlaylistComments(playlist_id : str, offset=0, limit=20 ,beforeTime=0):
    '''网页端 - 获取歌单评论

    Args:
        album_id (str): 歌单ID
        offset (int, optional): 时间顺序偏移数. Defaults to 0.
        limit (int, optional): 单次评论获取量. Defaults to 20.
        beforeTime (int, optional): 评论将从该时间戳（秒为单位）开始. Defaults to 0.

    Returns:
        dict
    '''
    return '/v1/resource/comments/A_PL_0_%s' % playlist_id,{'rid':str(playlist_id),'limit':str(limit),'offset':str(offset),'beforeTime':str(beforeTime * 1000)}

@LapiCryptoRequest
def GetTopPlaylists():
    '''Linux PC端 - 获取热门歌单

    Returns:
        dict
    '''
    return '/api/toplist',{}

@EapiCryptoRequest
def SetManipulatePlaylistTracks(trackIds,playlistId,op="add",imme=True,e_r=True):
    '''PC 端 - 操作歌单 - WIP - protected via 网易易盾

    TODO: defeat `watchman.js` obfuscation

    - op 有以下几种：
     - `add` : 添加到歌单
     - `del` : 从歌单删除
     
    Args:
        trackIds (list[str]): 待操作的歌曲ID列表
        playlistId ([int]): 要操作的歌单ID
        op (str, optional): 操作 . Defaults to "add".
        imme (bool, optional): 暂存. Defaults to True.
        e_r (bool, optional): 暂存. Defaults to True.

    Returns:
        [type]: [description]
    '''
    return '/api/v1/playlist/manipulate/tracks',{"trackIds":json.dumps(trackIds),"pid":str(playlistId),"op":op,"imme":str(imme).lower(),"e_r":str(e_r).lower()}