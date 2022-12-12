__desc__ = '''user.SetWeblog API 功能演示

摘自 https://github.com/Binaryify/NeteaseCloudMusicApi

    听歌打卡
    
    说明 : 调用此接口 , 传入音乐 id, 来源 id，歌曲时间 time，更新听歌排行数据

    必选参数 : id: 歌曲 id, sourceid: 歌单或专辑 id

    可选参数 : time: 歌曲播放时间,单位为秒

    接口地址 : /scrobble

    调用例子 : /scrobble?id=518066366&sourceid=36780169&time=291
'''
from __init__ import login
assert login(), "登录失败"
from pyncm.apis.user import SetWeblog
from pprint import pprint
print(__desc__)
pprint(SetWeblog(
    [{
        'action': 'play',
        'json': {
            'download': 0,
            'end': 'playend',
            'id': input('歌曲 ID:'),
            'sourceId': input('来源 ID:'),
            'time': input('时长:') or 300,
            'type': 'song',
            'wifi': 0,
            'source' : 'list',
        }
    }]
))
