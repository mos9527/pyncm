# PyNCM
NeteaseCloudMusic APIs for Python 3.x 适用于 Python 3 的网易云音乐 API

# 安装
    `pip install pyncm`

# 直接使用
API 可以通过命令行直接访问，请参照下列命令输出进行操作
    python -m pyncm -h

# 命令行使用说明
## 配置
- `pyncm config` 可以将输入的参数存储在 ~/.pyncm 中，一劳永逸
		python -m pyncm config --phone [your phone number] --password [your password] --output Downloads --clear-temp --quality lossless --logging-level 30
	- 解释
	`--phone --password` 登录令牌；将会以 cookie 的形式被保存
	`--output` 输出文件夹
	`--clear-temp` 自动清除下载临时文件
	`--quality` 下载质量
	`--logging-level` 日志过滤等级
	- **优先级:** 若在使用中设置了其他参数，命令行的参数会作为该会话的设置

## 使用
### 下载歌曲
`pyncm song --id [歌曲 ID]`
### 下载歌单
`pyncm playlist --id [歌单 ID]`
### 下载专辑
`pyncm album --id [专辑 ID]`
### 关于 ID
可通过网易云音乐的“分享链接”功能取得
如 `https://music.163.com/playlist?id=3199245372&userid=315542615`，该ID即为`3199245372`
其他功能详见 pyncm --help


# Python 使用示例
    from pyncm import NeteaseCloudMusic
    # 导入核心包
    NCM = NeteaseCloudMusic()
    # 获取歌曲信息    
    NCM.GetSongInfo(29732235)
    `{'data': [{'id': 29732235, 'url': 'http://m701.music.126.net/20200313090222/479f50d5748625d59d405c7a219f3f5b/jdyyaac/040f/565c ...`    
    # 获取歌曲详情
    NCM.GetSongDetail(29732235)    
    `{'songs': [{'name': 'Supernova', 'id': 29732235, 'pst': 0, 't': 0, 'ar': [{'id': 38725, 'name': 'Laszlo', 'tns': [], ...`
    # 获取歌曲评论
    NCM.GetSongComments(29732235)    
    `{'isMusician': False, 'userId': -1, 'topComments': [], 'moreHot': True, 'hotComments': [{'user': {'locationInfo': None, 'liveIn ...`

    详见 Wiki (WIP)

### 衍生项目

    [PyNCMd](https://github.com/greats3an/pyncmd) 