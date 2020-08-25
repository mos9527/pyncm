'''Video resoure related APIs'''
from . import WeapiCryptoRequest

@WeapiCryptoRequest
def GetMVDetail(mv_id:str):
    '''Retrives detailed infomation of one MV

    Args:
        mv_id (str): The MV's ID

    Returns:
        dict : Like count,view count and other stats
    '''
    return '/api/v1/mv/detail',{'id':str(mv_id)}

@WeapiCryptoRequest
def GetMVResource(mv_id:str, res=1080):
    '''Retrives URL of one MV's video resource

    Args:
        mv_id (str): The MV's ID
        res (int, optional): Can be 240 / 480 / 720 / 1080. Defaults to 1080.

    Returns:
        dict : URL,hash,etc
    '''
    return '/weapi/song/enhance/play/mv/url',{"id":str(mv_id),"r":str(res)}


@WeapiCryptoRequest
def GetMVComments(mv_id, offset=0, limit=20,total=False):   
    '''Retrives an MV's comments

    Args:
        mv_id (str): Album ID
        offset (int, optional): Where the first comment begins (ordered by time.ascending). Defaults to 0.
        limit (int, optional): How much comment to receive. Defaults to 20.
        total (bool, optional): Overrides said offset & limit,retrives entire comment list. Defaults to False
        
    Returns:
        dict: The filtered comments
    '''  
    return '/weapi/v1/resource/comments/R_MV_5_%s' % mv_id,{"rid":"R_MV_5_%s" % mv_id,"offset":str(offset),"total":str(total).lower(),"limit":str(limit)}