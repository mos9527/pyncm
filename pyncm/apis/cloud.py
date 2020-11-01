'''我的音乐云盘 - Cloud APIs'''
import json
from . import WeapiCryptoRequest,LoginRequiredApi,EapiCryptoRequest,Crypto,GetCurrentSession

@WeapiCryptoRequest
@LoginRequiredApi
def GetCloudDriveInfo(limit=30,offset=0):
    '''PC端 - 获取个人云盘内容

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
    '''PC端 - 获取个人云盘项目详情

    Args:
        song_ids (list): 云盘项目 ID

    Returns:
        dict
    '''
    ids = song_ids if isinstance(song_ids,list) else [song_ids]
    return '/weapi/v1/cloud/get/byids',{'songIds':ids}

@EapiCryptoRequest
def GetNosTokenAlloc(filename,md5,fileSize,ext,type='audio',nos_product=3,bucket='',local=False):
    '''移动端 - 云盘占位

    Args:
        filename (str): 文件名
        md5 (str): 文件 MD5
        fileSize (str): 文件大小
        ext (str): 文件拓展名
        type (str, optional): 上传类型. Defaults to 'audio'.
        nos_product (int, optional): APP类型. Defaults to 3.
        bucket (str, optional): 未知. Defaults to ''.
        local (bool, optional): 未知. Defaults to False.

    Returns:
        dict
    '''
    return '/eapi/nos/token/alloc',{"type":str(type),"nos_product":str(nos_product),"md5":str(md5),"local":str(local).lower(),"filename":str(filename),"fileSize":str(fileSize),"ext":str(ext),"bucket":str(bucket),"checkToken":Crypto.checkToken()}

@EapiCryptoRequest
def UploadCloudInfoV2(resourceId,songid,song,md5,filename,bitrate,album):
    return '/eapi/upload/cloud/info/v2',{"resourceId":str(resourceId),"songid":str(songid),"song":str(song),"md5":str(md5),"filename":str(filename),"bitrate":str(bitrate),"album":str(album),"checkToken":Crypto.checkToken()}

def UploadObject(stream,md5,fileSize,objectKey,token,offset=0,compete=True):
    '''移动端 - 上传云盘内容

    Args:
        stream : IOStream-like object
        md5 : 文件哈希
        objectKey : GetNosTokenAlloc 获得
        token : GetNosTokenAlloc 获得
        offset (int, optional): 续传起点. Defaults to 0.
        compete (bool, optional): 全部上传. Defaults to True.

    Returns:
        dict
    '''
    r = GetCurrentSession().post(
        'http://45.127.129.8/ymusic/' + objectKey.replace('/','%2F'),
        data=stream,
        params={
            'version':'1.0',
            'offset':offset,
            'complete':str(compete).lower()
        },
        headers={
            'x-nos-token':token,
            'Content-MD5':md5,
            'Content-Type':'audio/mpeg',
            'Content-Length':str(fileSize)
        }
    )
    return json.loads(r.text)