# -*- coding: utf-8 -*-
"""Helper utilites to aid operations w/ API responses"""
from threading import Lock
from functools import wraps
from os import listdir,path
import datetime,logging

truncate_length = 64
logger = logging.getLogger("pyncm.helper")

def SubstituteWithFullwidth(string,sub=set('\x00\\/:<>|?*".')):
    return "".join([c if not c in sub else chr(ord(c) + 0xFEE0) for c in string])

def Default(default=None):    
    def preWrapper(func):
        @property
        @wraps(func)
        def wrapper(*a, **k):
            try:
                return func(*a, **k)
            except Exception as e:
                logger.warn("Failed to get attribute %s : %s" % (func.__name__,e))
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

    def __init__(self,item_id,factory_func=None) -> None:
        # __init__ is always called after __new__
        if hasattr(self,'_lock'):
            with self._lock: # Ensure update's finished
                return
        # We only want to initialze once
        self._item_id = item_id
        if factory_func:
            self._factory_func = factory_func
        # Automatically update the dict once we finished loading
        self._lock = Lock()                
        # In case of race conditions when our info is still updating...
        return self.refresh()
    def refresh(self):
        with self._lock:
            self.data = self._factory_func(self._item_id)

class AlbumHelper(IDCahceHelper):
    def __init__(self, item_id):        
        from pyncm.apis.album import GetAlbumInfo
        super().__init__(item_id, GetAlbumInfo)
    
    def refresh(self):        
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
        return (
            datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=self.data["album"]["publishTime"])
        ).year

    @Default()
    def AlbumSongCount(self):
        """专辑歌曲数"""
        return self.data["album"]["size"]

    @Default()
    def AlbumArtists(self):
        """专辑艺术家"""
        return [_ar["name"] for _ar in self.data["album"]["artists"]]

class ArtistHelper(IDCahceHelper):
    def __init__(self, item_id):        
        from pyncm.apis.artist import GetArtistDetails
        super().__init__(item_id, GetArtistDetails)
    
    def refresh(self):        
        logger.debug('Caching artist info %s' % self._item_id)
        return super().refresh()

    @Default()
    def ID(self):
        """艺术家 ID"""
        return self.data["data"]["artist"]["id"]

    @Default()
    def ArtistName(self):
        """艺术家名"""
        return self.data["data"]["artist"]["name"]

    @Default()
    def ArtistTranslatedName(self):
        """艺术家翻译名"""
        return self.data["data"]["artist"]["transNames"]

    @Default()
    def ArtistBrief(self):
        """艺术家简述"""
        return self.data["data"]["artist"]["briefDesc"]    
    
class UserHelper(IDCahceHelper):
    def __init__(self, item_id):        
        from pyncm.apis.user import GetUserDetail
        super().__init__(item_id, GetUserDetail)
    
    def refresh(self):        
        logger.debug('Caching user info %s' % self._item_id)
        return super().refresh()

    @Default()
    def ID(self):
        """UID"""
        return self.data["userPoint"]["userId"]

    @Default()
    def UserName(self):
        """用户名"""
        return self.data["profile"]["nickname"]

    @Default()
    def Avatar(self):
        """头像"""
        return self.data["profile"]["avatarUrl"]

    @Default()
    def AvatarBackground(self):
        """主页背景"""
        return self.data["profile"]["backgroundUrl"]
    
class TrackHelper:
    """Helper class for handling generic track objects"""

    def __init__(self, track_dict) -> None:
        self.__dict__.update({"data":track_dict})

    @property
    def Duration(self) -> int:
        """歌曲时长 （毫秒）"""
        return int(self.data["dt"])

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
        return (
            datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=self.data["publishTime"] )
        ).year

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

    @Default(default="null")
    def CD(self):
        """专辑 CD"""
        return self.data["cd"]

    @Default()
    def Title(self):
        """保存名 [曲名] - [艺术家名 1,2...,n]"""
        return f'{self.TrackName} - {",".join(self.Artists)}'
    
    @property
    def template(self):
        """保存模板参数"""
        return {
            "id": str(self.ID),
            "year": str(self.TrackPublishTime),
            "no": str(self.TrackNumber),
            "track": self.TrackName,
            "album": self.AlbumName,
            "title": self.Title,
            "artists": " / ".join(self.Artists),
        }
class FuzzyPathHelper(IDCahceHelper):    
    tbl_basenames = None
    tbl_basenames_noext = None

    @property
    def base_path(self):
        return self._item_id

    def __init__(self, basepath, limit_exts={'.flac','.mp3','.m4a'}) -> None:
        self.limit_exts = limit_exts
        super().__init__(basepath)
    def _factory_func(self,_item_id):        
        # Make some hashtables w/ directory's file listing
        files = filter(lambda file:path.isfile(path.join(self.base_path,file)),listdir(self.base_path) if path.exists(self.base_path) else [])
        # 1. Table of basename
        self.tbl_basenames = {path.basename(file) for file in files}
        # 2. Table of basename w/o extension, but with the premise that the files themselves contain the extensions we want    
        split = lambda file:path.splitext(path.basename(file))
        self.tbl_basenames_noext = {(split(file)[0] if (split(file)[1].lower() in self.limit_exts) else None) for file in self.tbl_basenames}
        
    def exists(self,name,partial_extension_check=True):
        """Chcek if a file exists in O(1) time

        Args:
            name : File basename inside the FuzzyPathHelper's basepath
            partial_extension_check (bool, optional): Only check if the basename (w/o exts) matches.  Defaults to True.

        Notes:
            If limit_exts in the class constructor is set, this will limit the basename matching canidates to
            those with the selected exts only.    
        """
        if partial_extension_check:
            return name in self.tbl_basenames_noext
        else:
            return name in self.tbl_basenames