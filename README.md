# PyNCM
NeteaseCloudMusic APIs for Python 3.x 适用于 Python 3 的网易云音乐 API

# 直接使用
API 可以通过命令行直接访问，请参照下列命令输出进行操作
    pyncm.py -h

# Python 使用示例
    >>> from ncm.ncm_core import NeteaseCloudMusic
    # 导入核心包
    >>> NCM = NeteaseCloudMusic()
    >>> NCM.GetSongInfo(29732235)
    # 获取歌曲信息
    {'data': [{'id': 29732235, 'url': 'http://m701.music.126.net/20200313090222/479f50d5748625d59d405c7a219f3f5b/jdyyaac/040f/565c/0508/3ed3de2e4ea60ff52b6a2bc8a500f397.m4a', 'br': 96000, 'size': 3979843, 'md5': '3ed3de2e4ea60ff52b6a2bc8a500f397', 'code': 200, 'expi': 1200, 'type': 'm4a', 'gain': 0.0, 'fee': 8, 'uf': None, 'payed': 0, 'flag': 256, 'canExtend': False, 'freeTrialInfo': None, 'level': 'standard', 'encodeType': 'aac'}], 'code': 200}
    
    >>> NCM.GetSongDetail(29732235)
    # 获取歌曲详情
    {'songs': [{'name': 'Supernova', 'id': 29732235, 'pst': 0, 't': 0, 'ar': [{'id': 38725, 'name': 'Laszlo', 'tns': [], 'alias': []}], 'alia': [], 'pop': 80.0, 'st': 0, 'rt': None, 'fee': 8, 'v': 13, 'crbt': None, 'cf': '', 'al': {'id': 3069044, 'name': 'Supernova', 'picUrl': 'https://p2.music.126.net/lX7Tq41nF4VkYYeW_Tz1Wg==/109951163311252223.jpg', 'tns': [], 'pic_str': '109951163311252223', 'pic': 109951163311252223}, 'dt': 326844, 'h': {'br': 320000, 'fid': 0, 'size': 13075897, 'vd': -32900.0}, 'm': {'br': 192000, 'fid': 0, 'size': 7845555, 'vd': -30500.0}, 'l': {'br': 128000, 'fid': 0, 'size': 5230385, 'vd': -29600.0}, 'a': None, 'cd': '1', 'no': 1, 'rtUrl': None, 'ftype': 0, 'rtUrls': [], 'djId': 0, 'copyright': 2, 's_id': 0, 'mark': 393216, 'originCoverType': 0, 'mst': 9, 'cp': 729016, 'mv': 447041, 'rtype': 0, 'rurl': None, 'publishTime': 1415577600000}], 'privileges': [{'id': 29732235, 'fee': 8, 'payed': 0, 'st': 0, 'pl': 128000, 'dl': 0, 'sp': 7, 'cp': 1, 'subp': 1, 'cs': False, 'maxbr': 999000, 'fl': 128000, 'toast': False, 'flag': 256, 'preSell': False, 'playMaxbr': 999000, 'downloadMaxbr': 999000}], 'code': 200}

    >>> NCM.GetSongComments(29732235)
    # 获取歌曲评论
    {'isMusician': False, 'userId': -1, 'topComments': [], 'moreHot': True, 'hotComments': [{'user': {'locationInfo': None, 'liveInfo': None, 'expertTags': None, 'vipRights': None, 'vipType': 0, 'remarkName': None, 'userType': 0, 'nickname': 'MoeCity', 'experts': None, 'authStatus': 0, 'userId': 3445645, 'avatarUrl': 'https://p2.music.126.net/02UUU0SdRdIjhkx1OzXhTA==/19067730649247823.jpg'}...

# 说明

## 所包含的包

### ncm

ncm.ncm_core 即核心包，包含keygen和部分eapi，需要 pycryptodome 和 requests 运行

ncm.ncm_func 为功能包，需要上述包和 mutagen 和 colorama 运行

ncm.strings  包含所有非常量字符串，需要 colorama 以显示色彩

### utils

utils.clisheet CLI表格，用于显示下载进度

utils.downloader 纯标准库多线程下载器

utils.progressbar fork的一个进度条实现，作者为 'Carlos Alexandre S. da Fonseca'

# 工程进度
|功能|进度|函数名|
|-|-|-|
|明文登录（通过手机号及明文密码）|✔|NeteaseCloudMusic.UpdateLoginInfo|
|音频解析（无损解析需要以VIP特权登录）|✔|NeteaseCloudMusic.GetSongInfo|
|歌曲信息爬取|✔|~~NeteaseCloudMusic.GetExtraSongInfo~~NeteaseCloudMusic.GetSongDetail|
|歌词解析|✔|NeteaseCloudMusic.GetSongLyrics|
|歌单解析|✔|NeteaseCloudMusic.GetPlaylistInfo|
|歌曲评论爬取|✔|NeteaseCloudMusic.GetSongComments|
|专辑信息爬取|✔|NeteaseCloudMusic.GetAlbumInfo|
|专辑评论爬取|✔|NeteaseCloudMusic.GetAlbumComments|
|获取用户歌单|✔|NeteaseCloudMusic.GetUserPlaylists|
|MV信息爬取|✔|NeteaseCloudMusic.GetMVInfo|
|MV评论爬取|✔|NeteaseCloudMusic.GetMVComments|

|下载歌曲并填入 META|✔|NCMFunctions.DownloadSongAudio|
|批量下载专辑歌曲并填入 META|✔|NCMFunctions.DownloadAllSongsInAlbumAndMerge|
|批量下载歌单歌曲并填入 META|✔|NCMFunctions.DownloadAllSongsInPlaylistAndMerge|
|下载歌词并转换为多语言LRC|✔|NCMFunctions.DownloadAndFormatLyrics|

*大部分包都已详尽地注释过，如有疑问请提 issue*

## 依赖包

    (必须) requests,pycryptodome
    (可选) mutagen,colorama
