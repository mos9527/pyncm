# PyNCM Async

[![PyPI version](https://badge.fury.io/py/pyncm-async.svg)](https://badge.fury.io/py/pyncm-async)


提供异步支持的第三方 Python 网易云音乐 API

**注意** : 同步使用，请移步 [`sync` 分支](https://github.com/mos9527/pyncm/tree/master)

# **注意：长期支持状态** 
上游 API 变更、BUG 修复、安全更新等**有可能**得到及时响应；Feature Request 及非紧急 Issues 将被延后处理或不处理。

有意维护者请通过 GitHub Issues 联系获得 Collaborator 权限（不保证通过），或通过 Pull Request 贡献更改。

# 安装
    pip install pyncm-async

# API 使用示例
```python
>>> import asyncio
>>> from pyncm_async imoprt apis
>>> async def main():
>>>     # 获取歌曲信息
>>>     await apis.track.GetTrackAudio(29732235)
>>>     # 获取歌曲详情
>>>     await apis.track.GetTrackDetail(29732235)
>>>     # 获取歌曲评论
>>>     await apis.track.GetTrackComments(29732235)
>>> asyncio.run(main())
```

## Session
> `Session` 继承自 `httpx.AsyncClient`，用于异步执行网络请求。
在`pyncm_async` 中，`Session` 会受到内部管理，同时也支持用户自行管理。
如果希望自行管理 `Session` ，需要在调用 API 时显式传入 `session` 参数。
```python
# 由 pyncm_async 管理 Session
await GetAlbumInfo(album_id)
# 自行管理 Session
session = Session()
await GetAlbumInfo(album_id, session=session)
```

### Context Managers
`Session` 支持通过上下文管理器使用
```python
session = CreateNewSession()
# 进入该 Session, 在 `async with` 内的 API 将由该 Session 完成
async with session:
    await LoginViaCellPhone(...)
    result = await GetTrackAudio(...)
# 离开 Session. 此后 API 将继续由当前循环 Session 完成
await GetTrackComments(...)
```

### Session 管理策略
`httpx.AsyncClient` 是非异步安全的，继承自它的 `Session` 也同样非异步安全，因此 `pyncm_async` 需要对 `Session` 进行管理。

- 多事件循环管理策略

`pyncm_async` 默认每个事件循环 __有且只有一个__ 正在使用的 `Session`。

可以调用 `GetCurrentSession` 来获得所在循环 __正在使用的 `Session`__。

调用 `SetCurrentSession` 或 `SetNewSession` 可以刷新 __正在使用的 `Session`__。如果需要使用旧的 `Session`，请自行保存。

在 `pyncm_async` 进行管理时，无需考虑异步安全的问题；而如果要自行管理，需要确保调用 API 时传入的 `Session` 是在当前事件循环实例化的。

- 上下文管理器管理策略

`pyncm_async` 允许无限多个由上下文管理器实例化的 `Session`。

在上下文管理器的作用域内，`pyncm_async` 默认使用由该上下文管理器实例化的 `Session`。

在嵌套使用上下文管理器时，`pyncm_async` 会使用最内层的上下文管理器实例化的 `Session`。当然，这种做法是不推荐的，

#### 登录状态
`pyncm_async` 不支持自动同步 `Session` 的登录状态。

在切换事件循环、进入上下文管理器或执行其它任何会创建新 `Session` 的操作后，都需要重新加载登录态。

## API 说明
大部分 API 函数已经详细注释，可读性较高。推荐参阅 [API 源码](https://github.com/mos9527/pyncm/tree/async/pyncm_async) 获得支持

## 添加新API
`pyncm_async` 仅封装了常用且相对稳定的 API。如果需要使用更多 API，可以自行添加。

在添加新 API 时，需要明确以下5项内容：
- 是否返回原始响应内容
- API 来源  --Weapi/Eapi
- API 路径
- 请求参数  --必须为 `dict` 类型，即使无参数也需传入空字典 __{}__
- 请求方法  --默认为 `POST`，可空

如果返回原始响应内容，可以直接使用 `pyncm_async`提供的装饰器对 API 进行装饰，并遵循以下规范：
- API 须定义为 __同步__ 函数 (仍以异步调用，由装饰器内部实现)；
- API  __不应包含__ 关键字参数 `session` (调用时仍可使用此参数，由装饰器内部实现)；
- __不应标注__ 返回值类型 (返回`dict`， 由装饰器内部实现)。
```python
@WeapiCryptoRequest
def new_api(*args, **kwargs):
    path: str
    params: dict
    method: str
    ...
    return path, params, method
```
如需要对原始响应内容进行处理，可利用匿名函数 `lambda` 来实现，并遵循以下规范：
- API 须定义为 __异步__ 函数；
- API  __须包含__ 关键字参数 `session`；
- 返回字典类型的结果。

以下是一个最小化示例：
```python
async def new_api(*args,  session: Session = None, **kwargs) -> dict:
    session = session or GetCurrentSession()
    api_func = lambda : (path, params, method)
    request_func = EapiCryptoRequest(api_fnc)
    res = await request_func(session=session)
    ...
```



# FAQ
- 为什么 `GetTrackAudio` 几乎拿不到音频 URL？

你需要[进行登陆](https://github.com/mos9527/pyncm/blob/async/pyncm_async/apis/login.py)。若身边没有合适的账号，也可选择匿名登陆 (IPython内示例)：
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
