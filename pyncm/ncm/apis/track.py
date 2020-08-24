from . import WeapiCryptoRequest
from . import logger
import json
@WeapiCryptoRequest
def GetTrackDetail(song_ids):
    '''
        Fetches a song's 'detailed' infomation

            song_ids        :        ID of songs (e.g. [1234,5678] or 1234)
    '''
    ids = song_ids if isinstance(song_ids,list) else [song_ids]
    return '/weapi/v3/song/detail',{"c":json.dumps([{'id': str(id)} for id in ids])}

@WeapiCryptoRequest
def GetTrackAudio(song_ids, quality='lossless',encodeType='aac'):
    '''
        Fetches a song's info.By default,it only returns the url and non-meta info.
        
        `quality` can be : standard,higher,lossless
        `encodeType` is yet unknown,though `aac` is valiad
    '''
    if not quality in ['standard', 'higher', 'lossless']:
        logger.warn('Invalid quality config `%s`,falling back to `standard`')
        quality = 'standard'
    # Quality check
    ids = song_ids if isinstance(song_ids,list) else [song_ids]
    return '/weapi/song/enhance/player/url/v1',{"ids":ids,"level":quality,"encodeType":encodeType}


@WeapiCryptoRequest
def GetTrackLyrics(song_id):
    '''Fetches a song's lyrics'''
    return '/weapi/song/lyric',{"id": str(song_id), "lv": -1, "tv": -1}


@WeapiCryptoRequest
def GetTrackComments(song_id, offset=0, limit=20):
    '''
        Fetches a song's comments

            offset  :   sets where the comment begins
            limit   :   sets how many of them can be sent
    '''
    return '/weapi/v1/resource/comments/R_SO_4_%s' % song_id,{"rid":str(song_id),"offset":str(offset),"total":"true","limit":str(limit)}