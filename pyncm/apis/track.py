'''Track / Song related APIs'''
from . import WeapiCryptoRequest
from . import logger
import json
@WeapiCryptoRequest
def GetTrackDetail(song_ids : list):
    '''Retrive track(s)' detailed infomation

    Args:
        song_ids (list): A list of song IDs

    Returns:
        dict : The said detail
    '''
    ids = song_ids if isinstance(song_ids,list) else [song_ids]
    return '/weapi/v3/song/detail',{"c":json.dumps([{'id': str(id)} for id in ids])}

@WeapiCryptoRequest
def GetTrackAudio(song_ids:list, quality='lossless',encodeType='aac'):
    '''Fetches track(s)' audio URL

    Args:
        song_ids (list): A list of song IDs
        quality (str, optional): Can be standard / high / lossless . Defaults to 'lossless'.
        encodeType (str, optional): Audio encoder. Defaults to 'aac'.

    Returns:
        dict : The said URL
    '''
    if not quality in ['standard', 'higher', 'lossless']:
        logger.warn('Invalid quality config `%s`,falling back to `standard`')
        quality = 'standard'
    # Quality check
    ids = song_ids if isinstance(song_ids,list) else [song_ids]
    return '/weapi/song/enhance/player/url/v1',{"ids":ids,"level":quality,"encodeType":encodeType}


@WeapiCryptoRequest
def GetTrackLyrics(song_id : str):
    '''Get one track's lyrics

    Args:
        song_id (str): The ID of the track

    Returns:
        dict : The said lyrics
    '''
    return '/weapi/song/lyric',{"id": str(song_id), "lv": -1, "tv": -1}


@WeapiCryptoRequest
def GetTrackComments(song_id, offset=0, limit=20):
    '''Feteches one track's comments

    Args:
        song_id (str): The ID of the track
        offset (int, optional): Where the first comment begins (ordered by time.ascending). Defaults to 0.
        limit (int, optional): How much comment to receive. Defaults to 20.

    Returns:
        dict: The filtered comments
    '''
    return '/weapi/v1/resource/comments/R_SO_4_%s' % song_id,{"rid":str(song_id),"offset":str(offset),"total":"true","limit":str(limit)}