# -*- coding: utf-8 -*-
# PyNCM CLI interface

from pyncm import (
    DumpSessionAsString,
    GetCurrentSession,
    LoadSessionFromString,
    SetCurrentSession,
    __version__
)
from pyncm.utils.lrcparser import LrcParser
from pyncm.utils.yrcparser import YrcParser , ASSWriter , YrcLine , YrcBlock
from pyncm.utils.helper import TrackHelper,ArtistHelper,UserHelper,FuzzyPathHelper, SubstituteWithFullwidth
from pyncm.apis import artist, login, track, playlist, album , user
from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from time import sleep
from os.path import join, exists
from os import remove, makedirs

from logging import exception, getLogger, basicConfig
import sys, argparse, re , os
logger = getLogger('pyncm.main')
# Import checks
OPTIONALS = {"mutagen": False, "tqdm": False, "coloredlogs": False}
OPTIONALS_MISSING_INFO = {
    "mutagen": "无法为下载的音乐添加歌手信息，封面等资源",
    "tqdm": "将不会显示下载进度条",
    "coloredlogs": "日志不会以彩色输出",
}
from importlib.util import find_spec

for import_name in OPTIONALS:
    OPTIONALS[import_name] = find_spec(import_name)
    if not OPTIONALS[import_name]:
        sys.stderr.writelines(
            [f"[WARN] {import_name} 没有安装，{OPTIONALS_MISSING_INFO[import_name]}\n"]
        )

__desc__ = """PyNCM 网易云音乐下载工具 %s""" % __version__

# Key-Value classes
class BaseKeyValueClass:
    def __init__(self, **kw) -> None:
      for k, v in kw.items():
            self.__setattr__(k, v)


class TaskPoolExecutorThread(Thread):
    @staticmethod
    def tag_audio(track: TrackHelper, file: str, cover_img: str = ""):
        if not OPTIONALS["mutagen"]:
            return
        def write_keys(song):
            # Writing metadata
            # Due to different capabilites of containers, only
            # ones that can actually be stored will be written.
            complete_metadata = {
                "title" : [track.TrackName],
                "artist" : [*(track.Artists or [])],
                "albumartist" : [*(track.Album.AlbumArtists or [])],
                "album" : [track.AlbumName],
                "tracknumber" :  "%s/%s" % (track.TrackNumber,track.Album.AlbumSongCount),
                "date" : [str(track.Album.AlbumPublishTime)], # TrackPublishTime is not very reliable!
                "copyright": [track.Album.AlbumCompany or ""],
                "discnumber" : [track.CD],
                # These only applies to vorbis tags (e.g. FLAC)                
                "totaltracks" : [str(track.Album.AlbumSongCount)],
                "ncm-id":[str(track.ID)]
            }                    
            for k,v in complete_metadata.items():
                try:
                    song[k] = v
                except:
                    pass
            song.save()

        def mp4():
            from mutagen import easymp4
            from mutagen.mp4 import MP4, MP4Cover

            song = easymp4.EasyMP4(file)
            write_keys(song)
            if exists(cover_img):
                song = MP4(file)
                song["covr"] = [MP4Cover(open(cover_img, "rb").read())]
                song.save()

        def mp3():
            from mutagen.mp3 import EasyMP3,HeaderNotFoundError
            from mutagen.id3 import ID3, APIC
            try:
                song = EasyMP3(file)            
            except HeaderNotFoundError:
                song = EasyMP3()
                song.filename = file
                song.save()
                song = EasyMP3(file)            
            write_keys(song)
            if exists(cover_img):
                song = ID3(file)
                song.update_to_v23()  # better compatibility over v2.4
                song.add(
                    APIC(
                        encoding=3,
                        mime="image/jpeg",
                        type=3,
                        desc="",
                        data=open(cover_img, "rb").read(),
                    )
                )
                song.save(v2_version=3)

        def flac():
            from mutagen.flac import FLAC, Picture
            from mutagen.mp3 import EasyMP3
            song = FLAC(file)            
            write_keys(song)
            if exists(cover_img):
                pic = Picture()
                pic.data = open(cover_img, "rb").read()
                pic.mime = "image/jpeg"
                song.add_picture(pic)   
                song.save()

        def ogg():
            import base64
            from mutagen.flac import Picture
            from mutagen.oggvorbis import OggVorbis

            song = OggVorbis(file)            
            write_keys(song)
            if exists(cover_img):
                pic = Picture()
                pic.data = open(cover_img, "rb").read()
                pic.mime = "image/jpeg"
                song["metadata_block_picture"] = [
                    base64.b64encode(pic.write()).decode("ascii")
                ]
                song.save()

        format = file.split(".")[-1].upper()
        for ext, method in [
            ({"M4A", "M4B", "M4P", "MP4"}, mp4),
            ({"MP3"}, mp3),
            ({"FLAC"}, flac),
            ({"OGG", "OGV"}, ogg),
        ]:
            if format in ext:
                return method() or True
        return False

    def download_by_url(self, url, dest, xfer=False):
        # Downloads generic content
        response = GetCurrentSession().get(url, stream=True)
        length = int(response.headers.get("content-length"))

        with open(dest, "wb") as f:
            for chunk in response.iter_content(128 * 2**10):
                self.xfered += len(chunk)
                if xfer:
                    self.finished_tasks += len(chunk) / length  # task [0,1]
                f.write(chunk)  # write every 128KB read
        return dest

    def __init__(self, *a, max_workers=4, **k):
        super().__init__(*a, **k)
        self.daemon = True
        self.finished_tasks: float = 0
        self.xfered = 0
        self.task_queue = Queue()
        self.max_workers = max_workers

    def run(self):
        def execute(task: BaseKeyValueClass):
            if type(task) == MarkerTask:
                # Mark a finished task w/o execution                
                self.finished_tasks += 1
                return
            if type(task) == TrackDownloadTask:
                try:
                    # Downloding source audio
                    apiCall = track.GetTrackAudioV1 if not task.routine.args.use_download_api else track.GetTrackDownloadURLV1
                    if task.routine.args.use_download_api: logger.warning("使用下载 API，可能消耗 VIP 下载额度！")
                    dAudio = apiCall(task.audio.id, level=task.audio.level)
                    assert "data" in dAudio, "其他错误： %s" % dAudio
                    dAudio = dAudio['data']
                    if type(dAudio) == list:
                        dAudio = dAudio[0]
                    if not dAudio['url']:
                        # Attempt to give some sort of explaination
                        # 来自 https://neteasecloudmusicapi-docs.4everland.app/#/?id=%e8%8e%b7%e5%8f%96%e6%ad%8c%e6%9b%b2%e8%af%a6%e6%83%85
                        ''' fee : enum                       
                        0: 免费或无版权
                        1: VIP 歌曲
                        4: 购买专辑
                        8: 非会员可免费播放低音质，会员可播放高音质及下载
                        fee 为 1 或 8 的歌曲均可单独购买 2 元单曲
                        '''
                        fee = dAudio['fee']
                        assert fee != 0,"可能无版权"
                        assert fee != 1,"VIP歌曲，账户可能无权访问"
                        assert fee != 4,"歌曲所在专辑需购买"
                        assert fee != 8,"歌曲可能需要单独购买或以低音质加载"                        
                        assert False, "未知原因 (fee=%d)" % fee
                    logger.info(
                        "开始下载 #%d / %d - %s - %s - %skbps - %s"
                        % (
                            task.index + 1,
                            task.total,
                            task.song.Title,
                            task.song.AlbumName,
                            dAudio["br"] // 1000,
                            dAudio["type"].upper(),
                        )
                    )
                    task.extension = dAudio["type"].lower()
                    if not exists(task.audio.dest):
                        makedirs(task.audio.dest)
                    dest_src = self.download_by_url(
                        dAudio["url"],                        
                        task.save_as + "." + dAudio["type"].lower(),                    
                        xfer=True,
                    )
                    # Downloading cover
                    dest_cvr = self.download_by_url(
                        task.cover.url, task.save_as + '.jpg'
                    )
                    # Downloading & Parsing lyrics                    
                    lrc = LrcParser()
                    dLyrics = track.GetTrackLyricsNew(task.lyrics.id)
                    for k in set(dLyrics.keys()) & (
                        {"lrc", "tlyric", "romalrc"} - task.lyrics.lrc_blacklist
                    ):  # Filtering LRCs
                        lrc.LoadLrc(dLyrics[k]["lyric"])
                    lrc_text = lrc.DumpLyrics()
                    if lrc_text:
                        open(task.save_as + '.lrc', "w", encoding="utf-8").write(lrc_text)
                    # `yrc` (whatever that means) lyrics contains syllable-by-syllable time sigs                                        
                    if not 'yrc' in task.lyrics.lrc_blacklist and 'yrc' in dLyrics:
                        yrc = YrcParser(dLyrics['yrc']['version'],dLyrics['yrc']['lyric'])
                        parsed = yrc.parse()
                        writer = ASSWriter()

                        for line in parsed:
                            line : YrcLine
                            writer.begin_line(line.t_begin,line.t_end)
                            for block in line:
                                block : YrcBlock
                                if block.meta:
                                    writer.add_meta(YrcParser.extract_meta(block.meta))
                                else:
                                    writer.add_syllable(block.t_duration,block.text)
                            writer.end_line()

                        open(task.save_as + '.ass', "w", encoding="utf-8").write(writer.content)
                    # Tagging the audio
                    try:
                        self.tag_audio(task.song, dest_src, dest_cvr)
                    except Exception as e:
                        logger.warning("标签失败 - %s - %s" % (task.song.Title, e))
                    logger.info(
                        "完成下载 #%d / %d - %s" % (task.index + 1, task.total, task.song.Title)
                    )                
                except Exception as e:
                    logger.warning("下载失败 %s - %s" % (task.song.Title, e))
                    task.routine.result_exception(task.song.ID,e,task.song.Title)
                # Cleaning up
                remove(dest_cvr)

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while True:
                task = self.task_queue.get()
                future = executor.submit(execute, task)
                future.add_done_callback(lambda future: self.task_queue.task_done())


# Subroutines
class Subroutine:
    """Generic subroutine

    Subroutines are `callable`,upon called with `ids`,one
    queues tasks with all given arguments via `put_func` callback

    `prefix` is used to identify subroutines,especially when one is a child
    of another subroutine.
    """
    exceptions = None
    def __init__(self, args, put_func, prefix=None) -> None:
        self.args = args
        self.put = put_func        
        self.prefix = prefix or self.prefix
        self.exceptions = dict()

    def result_exception(self,result_id,exception : Exception,desc=None):
        self.exceptions.setdefault(result_id,list())
        self.exceptions[result_id].append((exception,desc))

    @property
    def has_exceptions(self):
        return len(self.exceptions) > 0
    
class BaseDownloadTask(BaseKeyValueClass):
    id: int
    url: str
    dest: str
    level : str


class LyricsDownloadTask(BaseDownloadTask):
    id: int
    dest: str
    lrc_blacklist: set


class TrackDownloadTask(BaseKeyValueClass):
    song: TrackHelper
    cover: BaseDownloadTask
    lyrics: BaseDownloadTask
    audio: BaseDownloadTask

    index: int
    total: int
    lyrics_exclude: set
    save_as: str
    extension: str

    routine : Subroutine

class MarkerTask(BaseKeyValueClass):
    pass

class Playlist(Subroutine):
    prefix = '歌单'
    """Base routine for ID-based tasks"""
    def filter(self, song_list):
        # This is only meant to faciliate sorting w/ APIs that doesn't implement them
        # The observed behaviors remains more or less the same with the offical ones
        if self.args.count > 0 and self.args.sort_by != 'default':
            sorting = {        
                'hot': lambda song : float(song['pop']), # [0,100.0]
                'time' : lambda song: TrackHelper(song).Album.AlbumPublishTime # in Years
            }[self.args.sort_by]
            song_list = sorted(song_list,key=sorting,reverse=not self.args.reverse_sort)
        return song_list[:self.args.count if self.args.count > 0 else len(song_list)]

    def forIds(self, ids):
        dDetails = [track.GetTrackDetail(ids[index:min(len(ids),index+1000)]).get("songs") for index in range(0,len(ids),1000)]
        dDetails = [song for stripe in dDetails for song in stripe]        
        dDetails = self.filter(dDetails)
        downloadTasks = []
        index = 0
        for index, dDetail in enumerate(dDetails):
            try:
                song = TrackHelper(dDetail)
                output_name=SubstituteWithFullwidth(
                    self.args.output_name.format(**song.template)
                )
                output_folder=self.args.output.format(**{
                    k:SubstituteWithFullwidth(v) for k,v in song.template.items()
                })
                    
                tSong = TrackDownloadTask(
                    index=index,
                    total=len(dDetails),
                    song=song,
                    cover=BaseDownloadTask(
                        id=song.ID, url=song.AlbumCover, dest=output_folder
                    ),
                    audio=BaseDownloadTask(
                        id=song.ID,
                        level=self.args.quality,
                        dest=output_folder,
                    ),
                    lyrics=LyricsDownloadTask(
                        id=song.ID,
                        dest=output_folder,
                        lrc_blacklist=set(self.args.lyric_no),
                    ),
                    save_as=join(output_folder,output_name),
                    routine=self
                )                                
                downloadTasks.append(tSong)
                # If audio file already exsists
                # Skip its download if `--no_overwrite` is explicitly set             
                if self.args.no_overwrite:
                    if FuzzyPathHelper(output_folder).exists(
                        output_name,partial_extension_check=True
                    ):
                        logger.warning(
                            "单曲 #%d / %d - %s - %s 已存在，跳过"
                            % (index + 1, len(dDetails), song.Title, song.AlbumName))
                        self.put(MarkerTask())
                        continue
                self.put(tSong)

            except Exception as e:                    
                logger.warning(
                    "单曲 #%d / %d - %s - %s 无法下载： %s"
                    % (index + 1, len(dDetails), song.Title, song.AlbumName, e)
                )                
                self.result_exception(song.ID,e,song.Title)
        return downloadTasks

    def __call__(self, ids):
        queued = []
        for _id in ids:
            dList = playlist.GetPlaylistInfo(_id)
            logger.info(self.prefix + "：%s" % dict(dList)["playlist"]["name"])
            queuedTasks = self.forIds([tid.get("id") for tid in dict(dList)["playlist"]["trackIds"]])
            queued += queuedTasks
        return queued

class Album(Playlist):
    prefix = '专辑'
    def __call__(self, ids):
        queued = []
        for _id in ids:
            dList = album.GetAlbumInfo(_id)
            logger.info(self.prefix + "：%s" % dict(dList)["album"]["name"])
            queuedTasks = self.forIds([tid["id"] for tid in dList["songs"]])
            queued += queuedTasks
        return queued

class Artist(Playlist):
    prefix = '艺术家'
    def __call__(self, ids):
        queued = []
        for _id in ids:        
            logger.info(self.prefix + "：%s" % ArtistHelper(_id).ArtistName)
            # dList = artist.GetArtisTracks(_id,limit=self.args.count,order=self.args.sort_by)
            # This API is rather inconsistent for some reason. Sometimes 'songs' list
            # would be straight out empty
            # TODO: Fix GetArtistTracks
            # We iterate all Albums instead as this would provide a superset of what `GetArtistsTracks` gives us   
            album_ids = [album['id'] for album in artist.GetArtistAlbums(_id)['hotAlbums']]
            album_task = Album(self.args,self.put,prefix='艺术家专辑')
            album_task.forIds = self.forIds
            # All exceptions will still be handled by this subroutine
            # TODO: Try to... handle this nicer?
            queued += album_task(album_ids)                        
        return queued

class User(Playlist):
    prefix = '用户'
    def __call__(self, ids):
        queued = []
        for _id in ids:
            logger.info(self.prefix + "： %s" % UserHelper(_id).UserName)
            logger.warning('同时下载收藏歌单' if self.args.user_bookmarks else '只下载该用户创建的歌单')
            playlist_ids = [
                pl['id'] for pl in user.GetUserPlaylists(_id)['playlist'] if self.args.user_bookmarks or pl['creator']['userId'] == UserHelper(_id).ID
            ]
            playlist_task = Playlist(self.args,self.put,prefix='用户歌单')
            playlist_task.forIds = self.forIds
            queued += playlist_task(playlist_ids)                        
        return queued

class Song(Playlist):
    def __call__(self, ids):
        queuedTasks = self.forIds(ids)
        if self.args.save_m3u:
            logger.warning("不能为单曲保存 m3u 文件")
        return queuedTasks
    
def create_subroutine(sub_type) -> Subroutine:
    """Dynamically creates subroutine callable by string specified"""
    return {"song": Song, "playlist": Playlist, "album": Album, "artist": Artist, "user": User}[sub_type]

def parse_sharelink(url):
    """Parses (partial) URLs for NE resources and determines its ID and type

    e.g.
        31140560 (plain song id)
        https://mos9527.github.io/pyncmd/?trackId=1818064296 (pyncmd)
        分享Ali Edwards的单曲《Devil Trigger》: http://music.163.com/song/1353163404/?userid=6483697162 (来自@网易云音乐) (mobile app)
        "分享mos9527创建的歌单「東方 PC」: http://music.163.com/playlist?id=72897851187" (desktop app)
        https://music.163.com/#/user/home?id=315542615 (user homepage)
    """
    rurl = re.findall("(?:http|https):\/\/.*", url)
    if rurl:
        url = rurl[0]  # Use first URL found. Otherwise use value given as is.
    numerics = re.findall("\d{4,}", url)    
    assert numerics != None, "未在链接中找到任何 ID"
    ids = numerics[:1]  # Only pick the first match
    table = {
        "song": ["trackId", "song"],
        "playlist": ["playlist"],
        "artist": ["artist"],
        "album": ["album"],
        "user" : ["user"]
    }
    rtype = "song"  # Defaults to songs (tracks)
    best_index = len(url)
    for rtype_, rkeyword in table.items():
        for kw in rkeyword:
            try:
                index = url.index(kw)
                if index < best_index:
                    best_index = index
                    rtype = rtype_                    
            except ValueError:
                continue                
    return rtype, ids


PLACEHOLDER_URL = "00000"

def parse_args(quit_on_empty_args=True):
    """Setting up __main__ argparser"""
    parser = argparse.ArgumentParser(
        description=__desc__, formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "url", metavar="链接", help="网易云音乐分享链接", nargs="*", default=PLACEHOLDER_URL
    )
    group = parser.add_argument_group("下载")
    group.add_argument(
        "--max-workers", "-m", metavar="最多同时下载任务数", default=4, type=int
    )
    group.add_argument(
        "--output-name",
        "--template",
        "-t",
        metavar="保存文件名模板",
        help=r"""保存文件名模板
    参数：    
        id     - 网易云音乐资源 ID
        year   - 出版年份
        no     - 专辑中编号
        album  - 专辑标题
        track  - 单曲标题        
        title  - 完整标题
        artists- 艺术家名
    例：
        {track} - {artists} 等效于 {title}""",
        default=r"{title}"
    )
    group.add_argument("-o","--output", metavar="输出", default=".", help=r"""输出文件夹
    注：该参数也可使用模板，格式同 保存文件名模板"""
    )
    group.add_argument(
        "--quality",
        metavar="音质",
        choices=['standard','exhigh','lossless','hires'],
        help=r"""音频音质（高音质需要 CVIP）
    参数：
        hires  - Hi-Res
        lossless- “无损”
        exhigh  - 较高
        standard- 标准""",
        default="standard",
    )
    group.add_argument(
        "-dl",
        "--use-download-api",
        action="store_true", 
        help="调用下载API，而非播放API进行下载。如此可能允许更高高音质音频的下载。\n【注意】此API有额度限制，参考 https://music.163.com/member/downinfo"
    )
    group.add_argument("--no-overwrite", action="store_true", help="不重复下载已经存在的音频文件")
    group = parser.add_argument_group("歌词")
    group.add_argument(
        "--lyric-no",
        metavar="跳过歌词",
        help=r"""跳过某些歌词类型的下载
    参数：        
        lrc    - 源语言歌词  (合并到 .lrc)
        tlyric - 翻译后歌词  (合并到 .lrc)
        romalrc- 罗马音歌词  (合并到 .lrc)
        yrc    - 逐词滚动歌词 (保存到 .ass)
        none   - 下载所有歌词
    例：
        --lyric-no "tlyric romalrc yrc" 将只下载源语言歌词
        --lyric-no none 将下载所有歌词
    注：
        默认不下载 *逐词滚动歌词*
        """,
        default="yrc",
    )
    group = parser.add_argument_group("登陆")
    group.add_argument("--phone", metavar="手机", default="", help="网易账户手机号")
    group.add_argument("--pwd", "--password", metavar="密码", default="", help="网易账户密码")
    group.add_argument("--save", metavar="[保存到]", default="", help="写本次登录信息于文件")
    group.add_argument(
        "--load", metavar="[保存的登陆信息文件]", default="", help="从文件读取登录信息供本次登陆使用"
    )
    group.add_argument("--http", action="store_true", help="优先使用 HTTP，不保证不被升级")
    group.add_argument("--deviceId", metavar="设备ID", default="", help="指定设备 ID；匿名登陆时，设备 ID 既指定对应账户\n【注意】默认 ID 与当前设备无关，乃从内嵌 256 可用 ID 中随机选取；指定自定义 ID 不一定能登录，相关性暂时未知")
    group.add_argument("--log-level", help="日志等级", default="NOTSET")
    group = parser.add_argument_group("限量及过滤（注：只适用于*每单个*链接 / ID）")
    group.add_argument("-n","--count",metavar="下载总量",default=0,help="限制下载歌曲总量，n=0即不限制（注：过大值可能导致限流）",type=int)
    group.add_argument(
        "--sort-by",
        metavar="歌曲排序",
        default="default",
        help="【限制总量时】歌曲排序方式 (default: 默认排序 hot: 热度高（相对于其所在专辑）在前 time: 发行时间新在前)",
        choices=["default", "hot","time"]
    )
    group.add_argument("--reverse-sort",action="store_true",default=False,help="【限制总量时】倒序排序歌曲")
    group.add_argument("--user-bookmarks",action="store_true",default=False,help="【下载用户歌单时】在下载用户创建的歌单的同时，也下载其收藏的歌单")
    group = parser.add_argument_group("工具")
    group.add_argument(
        "--save-m3u",
        metavar="保存M3U播放列表文件名",
        default="",
        help=r"""将本次下载的歌曲文件名依一定顺序保存在M3U文件中；写入的文件目录相对于该M3U文件
        文件编码为 UTF-8
        顺序为：链接先后优先——每个链接的所有歌曲依照歌曲排序设定 （--sort-by）排序"""
    )    
    args = parser.parse_args()
    # Clean up    
    args.lyric_no = args.lyric_no.lower()
    args.lyric_no = args.lyric_no.split(' ')
    if 'none' in args.lyric_no:
        args.lyric_no = []
    def print_help_and_exit():
        sys.argv.append("-h")  # If using placeholder, no argument is really passed
        sys.exit(__main__())  # In which case, print help and exit
    if args.url == PLACEHOLDER_URL and not args.save:
        if quit_on_empty_args:
            print_help_and_exit()
        else:
            return args,[]
    try:
        return args , [parse_sharelink(url) for url in args.url]
    except AssertionError:
        if args.url == PLACEHOLDER_URL:
            print_help_and_exit()
        assert args.save, "无效分享链接 %s" % ' '.join(args.url) # Allow invalid links for this one            
        return args , []

def __main__(return_tasks=False):    
    args , tasks = parse_args()    
    log_stream = sys.stdout
    # Getting tqdm & logger to work nicely together
    if OPTIONALS["tqdm"]:
        from tqdm.std import tqdm as tqdm_c

        class SemaphoreStdout:
            @staticmethod
            def write(__s):
                # Blocks tqdm's output until write on this stream is done
                # Solves cases where progress bars gets re-rendered when logs
                # spews out too fast
                with tqdm_c.external_write_mode(file=sys.stdout, nolock=False):
                    return sys.stdout.write(__s)

        log_stream = SemaphoreStdout
    if args.log_level == 'NOTSET':
        args.log_level = os.environ.get('PYNCM_DEBUG','INFO')
    if OPTIONALS["coloredlogs"]:
        import coloredlogs

        coloredlogs.install(
            level=args.log_level,
            fmt="%(asctime)s %(name)s [%(levelname).4s] %(message)s",
            stream=log_stream,
            isatty=True,
        )
    basicConfig(
        level=args.log_level, format="[%(levelname).4s] %(name)s %(message)s", stream=log_stream
    )    
    from pyncm.utils.constant import known_good_deviceIds
    from random import choice as rnd_choice
    GetCurrentSession().deviceId = rnd_choice(known_good_deviceIds)
    # Pick a random one that WILL work!    
    if args.deviceId:
        GetCurrentSession().deviceId = args.deviceId        
    if args.load:
        logger.info("读取登录信息 : %s" % args.load)
        SetCurrentSession(LoadSessionFromString(open(args.load).read()))
    if args.http:
        GetCurrentSession().force_http = True
        logger.warning("优先使用 HTTP")
    if args.phone and args.pwd:
        login.LoginViaCellphone(args.phone, args.pwd)
        logger.info(
            "账号 ：%s (VIP %s)"
            % (GetCurrentSession().nickname, GetCurrentSession().vipType)
        )
    if args.save:
        logger.info("保存登陆信息于 : %s" % args.save)
        open(args.save, "w").write(DumpSessionAsString(GetCurrentSession()))
        return 0
    if not GetCurrentSession().logged_in:                
        login.LoginViaAnonymousAccount()
        logger.info("以匿名身份登陆成功，deviceId=%s, UID: %s" % (GetCurrentSession().deviceId,GetCurrentSession().uid))
    executor = TaskPoolExecutorThread(max_workers=args.max_workers)
    executor.daemon = True
    executor.start()

    def enqueue_task(task):
        executor.task_queue.put(task)
    
    subroutines = []
    queuedTasks = []
    for rtype,ids in tasks:
        task_desc = "ID: %s 类型: %s" % (ids[0],{'album':'专辑','playlist':'歌单®','song':'单曲','artist':'艺术家','user':'用户'}[rtype])
        logger.info("处理任务 %s" % task_desc) 
        subroutine = create_subroutine(rtype)(args, enqueue_task)
        queuedTasks += subroutine(ids)  # Enqueue tasks
        subroutines.append((subroutine,task_desc))

    if OPTIONALS["tqdm"]:
        import tqdm

        _tqdm = tqdm.tqdm(
            bar_format="{desc}: {percentage:.1f}%|{bar}| {n:.2f}/{total_fmt} {elapsed}<{remaining}"
        )
        _tqdm.total = len(queuedTasks)

        def report():
            _tqdm.desc = _tqdm.format_sizeof(executor.xfered, suffix="B", divisor=1024)
            _tqdm.update(min(executor.finished_tasks, len(queuedTasks)) - _tqdm.n)
            return True

    else:

        def report():
            sys.stderr.write(
                f"下载中 : {executor.finished_tasks:.1f} / {len(queuedTasks)} ({(executor.finished_tasks * 100 / len(queuedTasks)):.1f} %,{executor.xfered >> 20} MB)               \r"
            )
            return True

    while executor.task_queue.unfinished_tasks >= 0:
        try:
            report() and sleep(0.5)
            if executor.task_queue.unfinished_tasks == 0:
                break
        except KeyboardInterrupt:
            break
    
    # Check final results
    # Thought: Maybe we should automatically retry these afterwards?
    failed_ids = dict()
    for routine,desc in subroutines:
        routine : Subroutine
        if routine.has_exceptions:
            logger.error('%s - 下载未完成' % desc)
            for exception_id , exceptions in routine.exceptions.items():
                failed_ids[exception_id] = True
                for exception in exceptions:
                    exception_obj, desc = exception
                    logger.warning('下载出错 ID: %s - %s%s' % (exception_id,exception_obj,' (%s)' % desc if desc else ''))

    if args.save_m3u:    
        output_name = args.save_m3u
        output_folder = os.path.dirname(output_name)

        with open(output_name,'w',encoding='utf-8') as f:
            f.write('#EXTM3U\n')
            for task in queuedTasks:
                task : TrackDownloadTask
                filePath = task.save_as + '.' + task.extension
                relPath = os.path.relpath(filePath,output_folder)
                f.write('#EXTINF:,\n')
                f.write(relPath)
                f.write('\n')
        logger.info('已保存播放列表至：%s' % output_name)

    if failed_ids:
        logger.error('你可以将下载失败的 ID 作为参数以再次下载')
        logger.error('所有失败的任务 ID: %s' % ' '.join([str(i) for i in failed_ids.keys()]))
    report()
    logger.info(f'任务完成率 {(executor.finished_tasks * 100 / max(1,len(queuedTasks))):.1f}%')
    # To get actually downloaded tasks, filter by exlcuding failed_ids against task.song.ID
    if return_tasks:
        return queuedTasks, failed_ids
    return


if __name__ == "__main__":
    __main__()
    sys.exit(0)
