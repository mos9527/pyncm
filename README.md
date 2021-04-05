![Logo](https://github.com/greats3an/pyncm/raw/master/demos/_logo.png)

# PyNCM

# 安装
    pip install pyncm

# 直接使用
    python -m pyncm -h

## 说明
    若 Python 环境已安装[Gooey](https://github.com/chriskiehl/Gooey),通过 `-m` 不带参数即启动GUI
![Gooey GUI..?](https://github.com/greats3an/pyncm/raw/master/demos/_gooey_demo.png)

### 使用示例
    python -m pyncm http://music.163.com/song?id=31140560 --phone... --password...
    python -m pyncm http://music.163.com/album?id=3111188&userid=315542615  ...  

其他功能详见 
- [Wiki](https://github.com/greats3an/pyncm/wiki)

- [Demo](https://github.com/greats3an/pyncm/tree/master/demos)

# API 使用示例
    >>> from pyncm import apis
    >>> # 获取歌曲信息    
    >>> apis.track.GetTrackAudio(29732235)
    	`{'data': [{'id': 29732235, 'url': 'http://m701.music...`
    >>> # 获取歌曲详情
    >>> apis.track.GetTrackDetail(29732235)    
    	`{'songs': [{'name': 'Supernova', 'id': 2...`
    >>> # 获取歌曲评论
    >>> apis.track.GetTrackComments(29732235)    
    	`{'isMusician': False, 'userId': -1, 'topComments': [], 'moreHot': True, 'hotComments': [{'user': {'locationInfo': None, 'liveIn ...`

## 已实现的算法，APIs
[Wiki - Pages](https://github.com/greats3an/pyncm/wiki) 

[Wiki - Cryptograhpy](https://github.com/greats3an/pyncm/wiki/%23---Cryptography)
# PR
[Wiki - Home](https://github.com/greats3an/pyncm/wiki) 
# Credit
[Android逆向——网易云音乐排行榜api(上)](https://juejin.im/post/6844903586879520775)

[Binaryify/NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi/blob/master/util/crypto.js)

### 衍生项目
[PyNCMd](https://github.com/greats3an/pyncmd)