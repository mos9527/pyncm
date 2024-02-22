![Logo](https://github.com/greats3an/pyncm/raw/master/demos/_logo.png)

# PyNCM Async!

# 安装
    pip install pyncm-async

# API 使用示例 (IPython)
```python
In [1]: from pyncm_async import apis
# 获取歌曲信息    
In [2]: await apis.track.GetTrackAudio(29732235)
Out[2]:
{'data': [{'id': 29732235, 'url': 'http://m701.music...
# 获取歌曲详情
In [3]: await apis.track.GetTrackDetail(29732235)    
Out[3]:
{'songs': [{'name': 'Supernova', 'id': 2...
# 获取歌曲评论
In [4]: await apis.track.GetTrackComments(29732235)    
Out[4]:
{'isMusician': False, 'userId': -1, 'topComments': [], 'moreHot': True, 'hotComments': [{'user': {'locationInfo': None, 'liveIn ...
```
- 多 Session 示例

```python
LoginViaEmail(...) 
# 利用全局 Session 完成该 API Call
session = CreateNewSession() # 建立新的 Session
await LoginViaEmail(...) 
async with CreateNewSession(): # 建立新的 Session，并进入该 Session, 在 `with` 内的 API 将由该 Session 完成
    await LoginViaCellPhone(...)
# 离开 Session. 此后 API 将继续由全局 Session 管理
await GetTrackComments(...)
```
使用 `with` 时...
- 注：Session 各*线程*独立，各线程利用 `with` 设置的 Session 不互相影响
- 注：Session 离开 `with` clause 时，**Session 会被销毁**，但不会影响全局 Session
- 注：Session 生命周期细节请参阅 https://www.python-httpx.org/async/

同时，你也可以在 API Call 中 指定 Session
```python
await GetTrackComments(..., session=session)
```

详见 [Session 说明](https://github.com/mos9527/pyncm/blob/async/pyncm/__init__.py#L35)
## API 说明
大部分 API 函数已经详细注释，可读性较高。推荐参阅 [API 源码](https://github.com/mos9527/pyncm/tree/async/pyncm) 获得支持

## FAQ
- 为什么 `GetTrackAudio` 几乎拿不到音频 URL？

你需要[进行登陆](https://github.com/mos9527/pyncm/blob/master/async/apis/login.py)。若身边没有合适的账号，也可选择匿名登陆 (IPython内示例)：
```python
In [1]: from pyncm_async.apis.login import LoginViaAnonymousAccount
In [2]: await LoginViaAnonymousAccount()
Out[2]:
{'tick': 1662870122.1159196,
 'content': {'code': 200,
  'userId': 8023914528,
  'createTime': 1662868134354,
  'profile': {'nickname': 'Ano...
```
# 感谢
[Android逆向——网易云音乐排行榜api(上)](https://juejin.im/post/6844903586879520775)

[Binaryify/NeteaseCloudMusicApi](https://github.com/Binaryify/NeteaseCloudMusicApi)

### 衍生项目
[PyNCMd](https://github.com/mos9527/pyncmd)
