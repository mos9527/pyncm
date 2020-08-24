from . import WeapiCryptoRequest
from . import logger

@WeapiCryptoRequest
def GetAlbumInfo(album_id):
    '''Fetches an album's info'''
    return '/weapi/v1/album/%s' % album_id,{}

@WeapiCryptoRequest
def GetAlbumComments(album_id, offset=0, limit=20):
    '''Fetches a album's comments'''
    return '/weapi/v1/resource/comments/R_AL_3_%s' % album_id,{"rid":"R_AL_3_%s" % album_id,"offset":str(offset),"total":"true","limit":str(limit)}
