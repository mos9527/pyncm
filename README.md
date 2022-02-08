![Logo](https://github.com/greats3an/pyncm/raw/master/demos/_logo.png)

# PyNCM

# 安装
    pip install pyncm
推荐同时安装 （若不考虑使用CLI则可忽略）
- `mutagen` : 为下载的音乐打上封面等
- `tqdm`    : 显示实时下载进度

# 使用
    python -m pyncm -h

    usage: __main__.py [-h] [--template 模板] [--quality 音质] [--output 输出] [--lyric-no 跳过歌词 [跳过歌词 ...]] [--phone 手机] [--pwd 密码] [--save [保存到]]
                    [--load [保存的登陆信息文件]]
                    链接

    PyNCM 网易云音乐下载工具

    positional arguments:
    链接                    网易云音乐分享链接

    optional arguments:
    -h, --help            show this help message and exit

    下载:
    --template 模板         保存文件名模板
                                参数：
                                    id     - 网易云音乐资源 ID
                                    year   - 出版年份
                                    no     - 专辑中编号
                                    album  - 专辑标题
                                    track  - 单曲标题
                                    title  - 完整标题
                                    artists- 艺术家名
                                例：
                                    {track} - {artists} 等效于 {title}
    --quality 音质          音频音质（高音质需要 CVIP）
                                参数：
                                    lossless - “无损”
                                    high     - 较高
                                    standard - 标准
    --output 输出           输出文件夹

    歌词:
    --lyric-no 跳过歌词 [跳过歌词 ...]
                            跳过某些歌词类型的合并
                                参数：
                                    lrc    - 源语言歌词
                                    tlyric - 翻译后歌词
                                    romalrc- 罗马音歌词
                                例：
                                    --lyric-no tlyric --lyric-no romalrc 将只下载源语言歌词

    登陆:
    --phone 手机            网易账户手机号
    --pwd 密码              网易账户密码
    --save [保存到]          写本次登录信息于文件
    --load [保存的登陆信息文件]    从文件读取登录信息供本次登陆使用

### 使用示例
    python -m pyncm http://music.163.com/song?id=31140560 --phone... --password...
    python -m pyncm http://music.163.com/album?id=3111188&userid=315542615  ...  

其他功能详见 
- [Wiki](https://github.com/greats3an/pyncm/wiki)

- [Demo](https://github.com/greats3an/pyncm/tree/master/demos)

# API 使用示例
```python
>>> from pyncm import apis
# 获取歌曲信息    
>>> apis.track.GetTrackAudio(29732235)
{'data': [{'id': 29732235, 'url': 'http://m701.music...
# 获取歌曲详情
>>> apis.track.GetTrackDetail(29732235)    
{'songs': [{'name': 'Supernova', 'id': 2...
# 获取歌曲评论
>>> apis.track.GetTrackComments(29732235)    
{'isMusician': False, 'userId': -1, 'topComments': [], 'moreHot': True, 'hotComments': [{'user': {'locationInfo': None, 'liveIn ...
```

## API 说明
[移步 Wiki](https://github.com/greats3an/pyncm/wiki/05---%E6%AD%8C%E6%9B%B2) 

# 感谢
[Android逆向——网易云音乐排行榜api(上)](https://juejin.im/post/6844903586879520775)

[Binaryify/NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)

### 衍生项目
[PyNCMd](https://github.com/greats3an/pyncmd)
