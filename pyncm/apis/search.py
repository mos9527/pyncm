'''Search API'''
from . import WeapiCryptoRequest
TYPE_SONG     = 1
TYPE_ALBUM    = 10
TYPE_ARTIST   = 100
TYPE_PLAYLIST = 1000
TYPE_USER     = 1002
TYPE_MV       = 1004
TYPE_LYRICS   = 1006
TYPE_DJ       = 1009
TYPE_VIDEO    = 1014
@WeapiCryptoRequest
def Search(keyword:str,type=TYPE_SONG,limit=30,offset=0):
    '''Search by keyword & type

    Args:
        keyword (str): The keyword
        type ([int, optional): Const denoted by 'TYPE_' in this module. Defaults to TYPE_SONG.
        limit (int, optional): How much to receive. Defaults to 30.
        offset (int, optional): Where shall the result begin. Defaults to 0.

    Returns:
        dict : The search result
    '''
    return '/weapi/cloudsearch/get/web',{'s':str(keyword),'type':str(type),'limit':str(limit),'offset':str(offset)}