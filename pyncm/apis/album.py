'''Album related APIs'''
from . import WeapiCryptoRequest

@WeapiCryptoRequest
def GetAlbumInfo(album_id : str):
    '''Retrives album's info

    Args:
        album_id ([str]): Album ID

    Returns:
        dict: The tracks,producers,and etc
    '''
    return '/weapi/v1/album/%s' % album_id,{}

@WeapiCryptoRequest
def GetAlbumComments(album_id : str, offset=0, limit=20):
    '''Retrives an album's comments

    Args:
        album_id (str): Album ID
        offset (int, optional): Where the first comment begins (ordered by time.ascending). Defaults to 0.
        limit (int, optional): How much comment to receive. Defaults to 20.

    Returns:
        dict: The filtered comments
    '''
    return '/weapi/v1/resource/comments/R_AL_3_%s' % album_id,{"rid":"R_AL_3_%s" % album_id,"offset":str(offset),"total":"true","limit":str(limit)}