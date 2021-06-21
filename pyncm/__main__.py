'''`__main__` entry for PyNCM'''
from pyncm import GetCurrentSession,__version__,logger
from pyncm.utils.lrcparser import LrcParser
from pyncm.utils.helper import TrackHelper
from pyncm.apis import login,track,playlist,album

from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from time import sleep
from os.path import join,exists
from os import remove,makedirs

from logging import getLogger,basicConfig
import sys,argparse

__desc__ = '''PyNCM 网易云音乐下载工具'''
max_workers = 4
    
BITRATES = {'standard':96000,'high':320000,'lossless':3200000}
# Key-Value classes
class BaseKeyValueClass:
    def __init__(self,**kw) -> None:
        for k,v in kw.items():self.__setattr__(k,v)

class BaseDownloadTask(BaseKeyValueClass):
    id : int
    url : str
    dest : str

class LyricsDownloadTask(BaseDownloadTask):
    id : int
    dest : str
    lrc_blacklist : set

class TrackDownloadTask(BaseKeyValueClass):
    song : TrackHelper    
    cover : BaseDownloadTask
    lyrics : BaseDownloadTask
    resource : BaseDownloadTask
    resource_info : dict
    lyrics_exclude : set
    save_as : str

class TaskPoolExecutorThread(Thread):
    @staticmethod
    def tag_audio(track : TrackHelper,file : str,cover_img : str = ''):
        def write_keys(song):
            # Write trackdatas
            song['title'] = track.TrackName
            song['artist'] = track.Artists
            song['album'] = track.AlbumName
            song['tracknumber'] = str(track.TrackNumber)
            song['date'] = str(track.TrackPublishTime)
            song.save()            
        def mp4():            
            from mutagen import easymp4
            from mutagen.mp4 import MP4, MP4Cover
            song = easymp4.EasyMP4(file)            
            write_keys(song)
            if exists(cover_img):
                song = MP4(file)                
                song['covr'] = [MP4Cover(open(cover_img, 'rb').read())]
                song.save()
        def mp3():            
            from mutagen.mp3 import EasyMP3
            from mutagen.id3 import ID3, APIC
            song = EasyMP3(file)
            write_keys(song)
            if exists(cover_img):
                song = ID3(file)
                song.update_to_v23() # better compatibility over v2.4
                song.add(APIC(encoding=3, mime='image/jpeg', type=3,
                                desc='Cover', data=open(cover_img, 'rb').read()))                                          
                song.save(v2_version=3)
        def flac():            
            from mutagen.flac import FLAC, Picture
            song = FLAC(file)
            write_keys(song)
            if exists(cover_img):
                pic = Picture()
                pic.data = open(cover_img, 'rb').read()
                pic.mime = 'image/jpeg'
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
                pic.data = open(cover_img, 'rb').read()
                pic.mime = 'image/jpeg'
                song["metadata_block_picture"] = [base64.b64encode(pic.write()).decode('ascii')]
                song.save()
        format = file.split('.')[-1].upper()
        for ext,method in [({'M4A', 'M4B', 'M4P','MP4'},mp4),({'MP3'},mp3),({'FLAC'},flac),({'OGG','OGV'},ogg)]:
            if format in ext:return method() or True
        return False        

    def download_by_url(self,url,dest,xfer=False):
        # Downloads generic content
        response = GetCurrentSession().get(url,stream=True)                        
        length = int(response.headers.get('content-length'))
        
        with open(dest,'wb') as f:
            for chunk in response.iter_content(1024 * 2 ** 10):
                self.xfered += len(chunk)
                if xfer:
                    self.finished_tasks += len(chunk) / length # task [0,1]
                f.write(chunk) # write every 1MB read            
        return dest

    def __init__(self,*a,**k):
        super().__init__(*a,**k)
        self.finished_tasks : float = 0
        self.xfered = 0        
        self.task_queue = Queue()

    def run(self):
        def execute(task : TrackDownloadTask):
            try:
                if not exists(task.resource.dest):makedirs(task.resource.dest)
                # Downloding source audio
                dest_src = self.download_by_url(task.resource.url,join(task.resource.dest,task.save_as+'.'+task.resource_info['type']),xfer=True)
                # Downloading cover
                dest_cvr = self.download_by_url(task.cover.url,join(task.cover.dest,'%s.jpg' % task.cover.id))
                # Downloading & Parsing lyrics
                dest_lrc = join(task.lyrics.dest,task.save_as + '.lrc')
                lrc    = LrcParser()
                dLyrics = track.GetTrackLyrics(task.lyrics.id)
                for k in set(dLyrics.keys()) & ({'lrc','tlyric','romalrc'} - task.lyrics.lrc_blacklist): # Filtering LRCs
                    lrc.LoadLrc(dLyrics[k]['lyric'])    
                lrc_text = lrc.DumpLyrics()                       
                if lrc_text:open(dest_lrc,'w',encoding='utf-8').write(lrc_text)
                # Tagging the audio
                self.tag_audio(task.song,dest_src,dest_cvr)
                # Cleaning up
                remove(dest_cvr)               
            except Exception as e:
                logger.warning('下载未完成 %s - %s' % (task.song.Title,e))
        with ThreadPoolExecutor(max_workers=max_workers) as executor:        
            while True:
                task = self.task_queue.get()            
                future = executor.submit(execute,task)
                future.add_done_callback(lambda future:self.task_queue.task_done())
# Subroutines
class Subroutine:
    '''Generic subroutine
    
    Subroutines are `callable`,upon called with `ids`,one
    queues tasks with all given arguments via `put_func` callback
    '''
    def __init__(self,args,put_func) -> None:
        self.args = args
        self.put = put_func

def create_subroutine(sub_type) -> Subroutine:
    '''Dynamically creates subroutine callable by string specified'''
    class Playlist(Subroutine):
        def forIds(self,ids):
            dDetails = track.GetTrackDetail(ids)['songs']
            dAudios   = track.GetTrackAudio(ids,bitrate=BITRATES[self.args.quality])['data']
            
            dDetails = sorted(dDetails,key=lambda song:song['id'])
            dAudios = sorted(dAudios,key=lambda song:song['id'])               
            queued = 0
            for dDetail,dAudio in zip(dDetails,dAudios):
                song = TrackHelper(dDetail)
                logger.info('单曲 #%d / %d - %s - %s (%dkbps) - %s' % (queued+1,len(dDetails),song.Title,song.AlbumName,dAudio['br'] // 1000,dAudio['type'].upper()))        
                tSong = TrackDownloadTask(
                    song = song,
                    cover = BaseDownloadTask(id=song.ID,url=song.AlbumCover,dest=self.args.output),                    
                    resource = BaseDownloadTask(id=song.ID,url=dAudio['url'],dest=self.args.output),
                    lyrics = LyricsDownloadTask(id=song.ID,dest=self.args.output,lrc_blacklist=set(self.args.lyric_no)),
                    resource_info = dAudio,
                    save_as = self.args.template.format(**{
                        'id':song.ID,
                        'year':song.TrackPublishTime,
                        'no': song.TrackNumber,
                        'track' : song.TrackName,
                        'album' : song.AlbumName,
                        'title' : song.SanitizedTitle,
                        'artists' : ' / '.join(song.Artists),
                    })
                )          
                self.put(tSong)
                queued += 1
            return queued
        def __call__(self,ids): 
            queued = 0           
            for _id in ids:
                dList = playlist.GetPlaylistInfo(_id)
                logger.info('歌单 ：%s' % dList['playlist']['name'])
                queued += self.forIds([tid['id'] for tid in dList['playlist']['trackIds']])
            return queued

    class Album(Playlist):
        def __call__(self,ids):    
            queued = 0    
            for _id in ids:    
                dList = album.GetAlbumInfo(_id)
                logger.info('专辑 ：%s' % dList['album']['name'])
                queued += self.forIds([tid['id'] for tid in dList['songs']])
            return queued

    class Song(Playlist):
        def __call__(self,ids):            
            return self.forIds(ids)

    return {
        'song':Song,'playlist':Playlist,'album':Album
    }[sub_type]

def parse_sharelink(url):
    import urllib.parse
    split = urllib.parse.urlsplit(url)
    dest  = split.path.split('/')[-1]
    query = urllib.parse.parse_qs(split.query)
    return dest,query

def parse_args():    
    '''Setting up __main__ argparser'''
    parser = argparse.ArgumentParser(description=__desc__, formatter_class=argparse.RawTextHelpFormatter)
    parser.add_argument('url',metavar='链接',help='网易云音乐分享链接')
    group = parser.add_argument_group('下载')
    group.add_argument('--template',metavar='模板',help=r'''保存文件名模板
    参数：    
        id     - 网易云音乐资源 ID
        year   - 出版年份
        no     - 专辑中编号
        album  - 专辑标题
        track  - 单曲标题        
        title  - 完整标题
        artists- 艺术家名
    例：
        {track} - {artists} 等效于 {title}''',default=r'{title}')
    group.add_argument('--quality',metavar='音质',choices=list(BITRATES.keys()),help=r'''音频音质（高音质需要 CVIP）
    参数：
        lossless - “无损”
        high     - 较高
        standard - 标准''',default='standard')
    group.add_argument('--output',metavar='输出',default='.',help='输出文件夹')
    group = parser.add_argument_group('歌词')
    group.add_argument('--lyric-no',metavar='跳过歌词',help=r'''跳过某些歌词类型的合并
    参数：
        lrc    - 源语言歌词
        tlyric - 翻译后歌词
        romalrc- 罗马音歌词
    例：
        --lyric-no tlyric --lyric-no romalrc 将只下载源语言歌词''', choices=['lrc','tlyric','romalrc'], default='',nargs='+')
    group = parser.add_argument_group('登陆')
    group.add_argument('--phone',metavar='手机',default='',help='网易账户手机号')
    group.add_argument('--pwd',metavar='密码',default='',help='网易账户密码')
    args = parser.parse_args()        
    dest,query = parse_sharelink(args.url)

    ids = query['id']
    dest = dest
                
    return ids,args,dest    

def __main__():
    ids,args,dest  = parse_args()
    if args.phone and args.pwd:        
        login.LoginViaCellphone(args.phone,args.pwd)
        logger.info('账号 ：%s (VIP %s)' % (
            GetCurrentSession().login_info['content']['profile']['nickname'],
            GetCurrentSession().login_info['content']['profile']['vipType'])
        )
    executor = TaskPoolExecutorThread()
    executor.setDaemon(True)
    executor.start()   
    
    def enqueue_task(task):        
        executor.task_queue.put(task)

    subroutine = create_subroutine(dest)(args,enqueue_task)
    total_queued = subroutine(ids) # Enqueue tasks
    
    import tqdm
    _tqdm = tqdm.tqdm(bar_format='已完成 {desc}: {percentage:.1f}%|{bar}| {n:.2f}/{total_fmt} [{elapsed}<{remaining}')
    _tqdm.total = total_queued
    def report():                        
        _tqdm.desc = _tqdm.format_sizeof(executor.xfered,suffix='B',divisor=1024)        
        _tqdm.update(min(executor.finished_tasks,total_queued) - _tqdm.n)
        return True    

    while executor.task_queue.unfinished_tasks >= 0:
        report() and sleep(.5)
        if executor.task_queue.unfinished_tasks == 0:break

    return 0

if __name__ == '__main__':
    logger = getLogger()
    basicConfig(level='INFO',format='[%(levelname).4s] %(message)s')    
    sys.exit(__main__())