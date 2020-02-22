# PyNCM
NeteaseCloudMusic APIs for Python 3.x 适用于 Python 3 的网易云音乐 API

## 直接使用

    __init__.py -h

## Python 使用示例

    >>> from ncm.ncm_core import NeteaseCloudMusic
    # 导入核心包
    >>> NCM = NeteaseCloudMusic()
    >>> NCM.GetSongInfo(29732235)
    # 获取歌曲信息
    {'data': [{'id': 29732235, 'url': 'http://m701.music.126.net/20200209190806/3da313a3a60493280779b3aed9c6c9d7/jdyyaac/040f/565c/0508/3ed3de2e4ea60ff52b6a2bc8a500f397.m4a', 'br': 96000, 'size': 3979843, 'md5': '3ed3de2e4ea60ff52b6a2bc8a500f397', 'code': 200, 'expi': 1200, 'type': 'm4a', 'gain': 0.0, 'fee': 8, 'uf': None, 'payed': 0, 'flag': 256, 'canExtend': False, 'freeTrialInfo': None, 'level': 'standard', 'encodeType': 'aac'}], 'code': 200}

    >>> NCM.GetExtraSongInfo(29732235)
    # 获取附加歌曲信息
    {'title': 'Supernova', 'cover': 'http://p1.music.126.net/lX7Tq41nF4VkYYeW_Tz1Wg==/109951163311252223.jpg', 'author': 'Laszlo', 'album': 'Supernova', 'album_id': '3069044', 'artist_id': '38725'}

    >>> NCM.GetSongComments(29732235)
    # 获取歌曲评论
    {'isMusician': False, 'userId': -1, 'topComments': [], 'moreHot': True, 'hotComments': [{'user': {'locationInfo': None, 'liveInfo': None, 'expertTags': None, 'vipRights': None, 'vipType': 0, 'remarkName': None, 'userType': 0, 'nickname': 'MoeCity', 'experts': None, 'authStatus': 0, 'userId': 3445645, 'avatarUrl': 'https://p2.music.126.net/02UUU0SdRdIjhkx1OzXhTA==/19067730649247823.jpg'}...