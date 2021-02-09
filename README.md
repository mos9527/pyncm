![Logo](https://github.com/greats3an/pyncm/raw/master/demos/_logo.png)

# PyNCM

# 安装
    pip install pyncm

# 直接使用
    python -m pyncm -h
## 说明
### 配置
- `pyncm config` 会将本次输入参数存储于 `~/.pyncm`

		python -m pyncm config [arguments]
	- 存储的参数


| 参数  | 说明  |
| ------------ | ------------ |
|`--phone --password`| 登录令牌；只会保存登录cookie|
|`--output` | 输出文件夹|
| `--clear-temp`| 自动清除下载临时文件|
|`--quality`| 下载质量|
|`--logging-level` |日志过滤等级 |
- **优先级:** 若在使用中设置了其他参数，命令行的参数会作为该会话的设置
- 存储的参数均已加密
- 文件保存在 `~/.pyncm` 中

### 使用示例
#### 下载歌曲
`pyncm song --id [歌曲 ID]`
#### 下载歌单
`pyncm playlist --id [歌单 ID]`
#### 下载专辑
`pyncm album --id [专辑 ID]`

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