'''Playlist related APIs'''
from . import LapiCryptoRequest, WeapiCryptoRequest

@WeapiCryptoRequest
def GetPlaylistInfo(playlist_id,offset=0,total=True,limit=1000):
    '''Fetches a playlist's content'''
    return '/weapi/v6/playlist/detail',{"id":str(playlist_id),"offset":str(offset),"total":str(total).lower(),"limit":str(limit)}

@WeapiCryptoRequest
def GetPlaylistComments(playlist_id : str, offset=0, limit=20 ,beforeTime=0):
    '''Retrives a playlist's comments

    Args:
        playlist_id (str): Playlist ID
        offset (int, optional): Where the first comment begins (ordered by time.ascending). Defaults to 0.
        limit (int, optional): How much comment to receive. Defaults to 20.
        beforeTime (int,optional): Filter out any comment that's after this UNIX timestamp
        
    Returns:
        dict: The filtered comments
    '''
    return '/v1/resource/comments/A_PL_0_%s' % playlist_id,{'rid':str(playlist_id),'limit':str(limit),'offset':str(offset),'beforeTime':str(beforeTime)}

@LapiCryptoRequest
def GetTopPlaylists():
    '''Retrives all top-listened playlists

    Returns:
        dict : The said playlists
    '''
    return '/api/toplist',{}
