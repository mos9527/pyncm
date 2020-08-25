'''Cloud drive related APIs'''
from . import WeapiCryptoRequest
from .user import LoginRequiredApi

@WeapiCryptoRequest
@LoginRequiredApi
def GetCloudDriveInfo(limit=30,offset=0):
    '''Retrives YOUR OWN cloud drive's content

    Args:
        limit (int, optional): How much tracks to fetch. Defaults to 30.
        offset (int, optional): Where the indexed track begins,chronological. Defaults to 0.

    Returns:
        dict : Your tracks
    '''
    return '/weapi/v1/cloud/get',{limit:str(limit),offset:str(offset)}

@WeapiCryptoRequest
@LoginRequiredApi
def GetCloudDriveItemInfo(song_ids:list):
    '''Retrives info of songs of YOUR OWN cloud drive

    Args:
        song_ids (list): A list of song IDs

    Returns:
        dict : The track's info
    '''
    ids = song_ids if isinstance(song_ids,list) else [song_ids]
    return '/weapi/v1/cloud/get/byids',{'songIds':ids}