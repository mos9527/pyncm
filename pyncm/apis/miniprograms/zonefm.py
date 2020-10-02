'''私享云FM - Cloud FM APIs

`zone`即分区，已知的分区有
- `CLASSICAL` 古典
'''

from . import EapiCryptoRequest

@EapiCryptoRequest
def GetFmZoneInfo(limit=3,zone="CLASSICAL",header={},e_r=True):
    '''获取电台内容

    Args:
        limit (int, optional): 获取数目. Defaults to 3.
        zone (str, optional): 分区. Defaults to "CLASSICAL".
        header (dict, optional): [未知]. Defaults to {}.
        e_r (bool, optional): [未知]. Defaults to True.

    Returns:
        dict
    '''
    return 'http://interface3.music.163.com/eapi/zone/fm/get',{"limit":str(limit),"zone":zone,"header":str(header),"e_r":str(e_r).lower()}

@EapiCryptoRequest
def SetSkipFmTrack(id,zone="CLASSICAL",header={},e_r=True):
    '''跳过电台歌曲

    Args:
        id (int): 歌曲ID
        zone (str, optional): 分区. Defaults to "CLASSICAL".
        header (dict, optional): [未知]. Defaults to {}.
        e_r (bool, optional): [未知]. Defaults to True.

    Returns:
        dict
    '''
    return 'http://interface3.music.163.com/eapi/zone/fm/skip',{"songId":str(id),"zone":zone,"header":str(header),"e_r":str(e_r).lower(),"alg":"CLSalternate","time":"0"}
