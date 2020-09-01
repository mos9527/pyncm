'''我的音乐云盘 - Cloud APIs'''
from . import WeapiCryptoRequest,LoginRequiredApi

@WeapiCryptoRequest
@LoginRequiredApi
def GetCloudDriveInfo(limit=30,offset=0):
    '''获取个人云盘内容

    Args:
        limit (int, optional): 单次获取量. Defaults to 30.
        offset (int, optional): 获取偏移数. Defaults to 0.

    Returns:
        dict
    '''
    return '/weapi/v1/cloud/get',{limit:str(limit),offset:str(offset)}

@WeapiCryptoRequest
@LoginRequiredApi
def GetCloudDriveItemInfo(song_ids:list):
    '''获取个人云盘项目详情

    Args:
        song_ids (list): 云盘项目 ID

    Returns:
        dict
    '''
    ids = song_ids if isinstance(song_ids,list) else [song_ids]
    return '/weapi/v1/cloud/get/byids',{'songIds':ids}