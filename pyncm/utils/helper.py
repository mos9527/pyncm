# -*- coding: utf-8 -*-
"""Helper utilites to aid operations w/ API responses"""
import time
truncate_length = 64

def Default(default=None):
    def preWrapper(func):
        @property
        def wrapper(*a, **k):
            try:
                return func(*a, **k)
            except:
                return default
        return wrapper
    return preWrapper

class IDCahceHelper:
    """Generic cache for pesudo-static ID-based dicts"""
    _cache = dict()
    def __new__(cls,item_id,*args):
        if not item_id in IDCahceHelper._cache:            
            IDCahceHelper._cache[item_id] = super().__new__(cls)
        return IDCahceHelper._cache[item_id]
    def __init__(self,item_id,factory_func) -> None:
        # __init__ is always called after __new__
        if hasattr(self,'_item_id'):
            return
        # We only want to initialze once
        self._item_id = item_id
        self._factory_func = factory_func
        # Automatically update the dict once we finished loading
        return self.refresh()
    def refresh(self):
        self.__dict__.update({"data":self._factory_func(self._item_id)})

class AlbumHelper(IDCahceHelper):
    def __init__(self, item_id):        
        from pyncm.apis.album import GetAlbumInfo
        super().__init__(item_id, GetAlbumInfo)
    
    def refresh(self):
        from pyncm import logger
        logger.debug('Caching album info %s' % self._item_id)
        return super().refresh()

    @Default()
    def AlbumName(self):
        """专辑名"""
        return self.data["album"]["name"]

    @Default()
    def AlbumAliases(self):
        """专辑别名"""
        return self.data["album"]["alias"]

    @Default()
    def AlbumCompany(self):
        """专辑发行"""
        return self.data["album"]["company"]

    @Default()
    def AlbumBreifDescription(self):
        """专辑概述"""
        return self.data["album"]["breifDesc"]

    @Default()
    def AlbumDescription(self):
        """专辑说明"""
        return self.data["album"]["description"]

    @Default()
    def AlbumPublishTime(self):
        """专辑发布年份"""
        epoch = (
            self.data["album"]["publishTime"] / 1000
        )
        return time.gmtime(epoch).tm_year

    @Default()
    def AlbumSongCount(self):
        """专辑歌曲数"""
        return self.data["album"]["size"]

    @Default()
    def AlbumArtists(self):
        """专辑艺术家"""
        return [_ar["name"] for _ar in self.data["album"]["artists"]]
    
class TrackHelper:
    """Helper class for handling generic track objects"""

    def __init__(self, track_dict) -> None:
        self.__dict__.update({"data":track_dict})

    @property
    def Album(self) -> AlbumHelper:
        """专辑对象，会有更多歌曲元数据"""
        return AlbumHelper(self.data["al"]["id"])
    
    @Default()
    def ID(self):
        """网易云音乐 ID"""
        return self.data["id"]

    @Default()
    def TrackPublishTime(self):
        """歌曲发布年份"""
        epoch = (
            self.data["publishTime"] / 1000
        )  # stored as unix timestamp though only the year was ever useful
        return time.gmtime(epoch).tm_year

    @Default()
    def TrackNumber(self):
        """歌曲编号 （于专辑）"""
        return self.data["no"]

    @Default(default="Unknown")
    def TrackName(self):
        """歌曲名"""
        assert self.data["name"] != None
        return self.data["name"]

    @Default(default=[])
    def TrackAliases(self):
        """歌曲别名"""
        return self.data["alia"]

    @Default(default="Unknown")
    def AlbumName(self):
        """专辑名"""
        if self.data["al"]["id"]:
            return self.data["al"]["name"]
        else:
            return self.data["pc"]["alb"]

    @Default(
        default="https://p1.music.126.net/UeTuwE7pvjBpypWLudqukA==/3132508627578625.jpg"
    )
    def AlbumCover(self):
        """专辑封面"""
        al = self.data["al"] if "al" in self.data else self.data["album"]
        if al["id"]:
            return al["picUrl"]
        else:
            return "https://music.163.com/api/img/blur/" + self.data["pc"]["cid"]
            # source:PC version's core.js

    @Default(default=["Various Artists"])
    def Artists(self):
        """艺术家名 List"""
        ar = self.data["ar"] if "ar" in self.data else self.data["artists"]
        ret = [_ar["name"] for _ar in ar]
        if not ret.count(None):
            return ret
        else:
            return [self.data["pc"]["ar"]]  # for NCM cloud-drive stored audio

    @Default()
    def Title(self):
        """保存名 [曲名] - [艺术家名 1,2...,n]"""
        return f'{self.TrackName} - {",".join(self.Artists)}'

    _illegal_chars = set('\x00\\/:<>|?*')
    @Default()
    def SanitizedTitle(self):
        """兼容文件系统的保存名，
        文件名中若有 Windows 非法字符的存在，这些字符将会被替换为全角版本。
        其次，文件名长度也被限制在 200 字符以内
        """

        def _T(s, l=100):
            return "".join(
                [c if not c in self._illegal_chars else chr(ord(c) + 0xFEE0) for c in s]
            )[:l]

        return f'{_T(self.TrackName,100)} - {_T(",".join(self.Artists),100)}'
