'''网易云搜索 - Cloudsearch APIs'''
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
def GetSearchResult(keyword:str,type=TYPE_SONG,limit=30,offset=0):
    '''网页端 - 搜索某类型关键字

    Args:
        keyword (str): 搜索关键字
        type ([int, optional): 搜索类型，请使用本模块内 TYPE_... 之一 Defaults to TYPE_SONG.
        limit (int, optional): 单次获取量. Defaults to 30.
        offset (int, optional): 获取偏移数. Defaults to 0.

    Returns:
        dict
    '''
    return '/weapi/cloudsearch/get/web',{'s':str(keyword),'type':str(type),'limit':str(limit),'offset':str(offset)}