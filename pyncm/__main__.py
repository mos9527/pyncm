'''`__main__` entry for PyNCM'''
from logging import getLogger,basicConfig
from pyncm import GetCurrentSession,__version__
from pyncm.utils.lrcparser import LrcParser
from pyncm.utils.helper import TrackHelper
from pyncm.apis import login,track,playlist,album

from queue import Queue
from concurrent.futures import ThreadPoolExecutor
from threading import Thread
from time import sleep
from os.path import join,exists
from os import remove
from urllib.parse import urlparse,parse_qs

import sys,argparse,base64,re
__desc__ = '''PyNCM Netease Cloudmusic Utility'''
max_workers = 4
# Detect gooey
try:
    from gooey import Gooey,GooeyParser
    gooey_installed = True    
except:
    gooey_installed = False

class MultiParser(argparse.ArgumentParser):
    '''Handy parser for supporting both `Gooey` and legacy CLI'''
    WHITELIST = {'add_argument','gooey_installed','parser'}
    ARGUMENT_WHITELIST = {'widget'}
    def __init__(self) -> None:
        if gooey_installed:
            self.parser = GooeyParser(description=__desc__)
        else:
            self.parser = argparse.ArgumentParser(description=__desc__, formatter_class=argparse.RawTextHelpFormatter)
    def add_argument(self, *args, **kwargs):
        """
        add_argument(dest, ..., name=value, ...)
        add_argument(option_string, option_string, ..., name=value, ...)
        """
        gooey_whitelist = MultiParser.ARGUMENT_WHITELIST        
        self.parser.add_argument(*args,**dict(filter(lambda v:gooey_installed or not v[0] in gooey_whitelist,kwargs.items())))
    def __setattr__(self, name: str, value) -> None:
        if name in MultiParser.WHITELIST:
            return super().__setattr__(name,value)        
        self.parser.__setattr__(name,value)
    def __getattribute__(self, name: str):
        if name in MultiParser.WHITELIST:
            return super().__getattribute__(name)
        return self.parser.__getattribute__(name)

class BaseKeyValueClass:
    def __init__(self,**kw) -> None:
        for k,v in kw.items():self.__setattr__(k,v)

class BaseDownloadTask(BaseKeyValueClass):
    id : int
    url : str
    dest : str

class NETrackDownloadTask(BaseKeyValueClass):
    song : TrackHelper    
    cover : BaseDownloadTask
    lyrics : BaseDownloadTask
    resource : BaseDownloadTask
    resource_info : dict

class Subroutine:
    def setup_parser(self,parser : MultiParser):pass
    def entry(self,args):pass
    
BITRATES = {'standard':96000,'high':320000,'lossless':3200000}
class Song(Subroutine):
    __subcommand__ = 'song'
    def entry(self, args):
        dSong = track.GetTrackDetail([match_id(args.url)])['songs'][0]
        song = TrackHelper(dSong)        
        dAudio = track.GetTrackAudio([match_id(args.url)],BITRATES[args.quality])['data'][0]
        logger.info('单曲 - %s - %s (%dkbps)' % (song.Title,song.AlbumName,dAudio['br'] // 1000))        
        tSong = NETrackDownloadTask(
            song = song,
            cover = BaseDownloadTask(id=song.ID,url=song.AlbumCover,dest=args.output),
            lyrics = BaseDownloadTask(id=song.ID,dest=args.output),
            resource = BaseDownloadTask(id=song.ID,url=dAudio['url'],dest=args.output),
            resource_info = dAudio
        )
        queue_task(tSong)
        logger.info('下载任务已分配完成')
        return 1 # we queued 1 track for this

class Playlist(Subroutine):
    __subcommand__ = 'playlist'
    def forIds(self,ids,args):
        dDetails = track.GetTrackDetail(ids)['songs']
        dAudios   = track.GetTrackAudio(ids,BITRATES[args.quality])['data']
        
        dDetails = sorted(dDetails,key=lambda song:song['id'])
        dAudios = sorted(dAudios,key=lambda song:song['id'])               
        queued = 0
        for dDetail,dAudio in zip(dDetails,dAudios):
            song = TrackHelper(dDetail)
            logger.info('歌单 / 专辑单曲 #%d / %d - %s - %s (%dkbps)' % (queued+1,len(dDetails),song.Title,song.AlbumName,dAudio['br'] // 1000))        
            tSong = NETrackDownloadTask(
                song = song,
                cover = BaseDownloadTask(id=song.ID,url=song.AlbumCover,dest=args.output),
                lyrics = BaseDownloadTask(id=song.ID,dest=args.output),
                resource = BaseDownloadTask(id=song.ID,url=dAudio['url'],dest=args.output),
                resource_info = dAudio
            )          
            queued += queue_task(tSong)
        return queued
    def entry(self, args):
        dList = playlist.GetPlaylistInfo(match_id(args.url))
        logger.info('歌单   ：%s' % dList['playlist']['name'])
        return self.forIds([tid['id'] for tid in dList['playlist']['trackIds']],args)

class Album(Playlist):
    __subcommand__ = 'album'
    def entry(self, args):
        dList = album.GetAlbumInfo(match_id(args.url))
        logger.info('专辑   ：%s' % dList['album']['name'])
        return self.forIds([tid['id'] for tid in dList['songs']],args)

subs = {'song':Song(),'playlist':Playlist(),'album':Album()}

task_queue = Queue()
def queue_task(task : NETrackDownloadTask):        
    task_queue.put(task)
    return True

def parse_args():    
    '''Setting up __main__ argparser'''
    parser = MultiParser()
    parser.add_argument('url',metavar='链接',help='网易云音乐分享链接')
    group = parser.add_argument_group('下载')
    group.add_argument('--quality',metavar='音质',choices=list(BITRATES.keys()),help='音频音质（高音质需要 CVIP）',default='standard')
    group.add_argument('--output',metavar='输出',default='.',help='输出文件夹',widget='DirChooser')        
    group = parser.add_argument_group('登陆')
    group.add_argument('--phone',metavar='手机',default='',help='网易账户手机号')
    group.add_argument('--password',metavar='密码',default='',help='网易账户密码')
    args = parser.parse_args()
    # Parsing URL
    url = urlparse(args.url)
    qs = parse_qs(url.query)
    path = url.path.split('/')[-1].lower()
    if not path in subs:
        raise NotImplementedError(path)
    args.url = qs.get('id')[0]
    args.func = subs[path].entry
    return args    

def match_id(s):
    if type(s) is int:return s
    return int(re.compile('\d{5,}').match(s).group())

def tag(tHelper : TrackHelper,audio : str,cover : str):
    from mutagen.flac import FLAC, Picture
    from mutagen.id3 import ID3, APIC
    from mutagen.mp3 import EasyMP3
    from mutagen import easymp4
    from mutagen.mp4 import MP4, MP4Cover
    from mutagen.oggvorbis import OggVorbis    
    def write_keys(song):
        # Write trackdatas
        song['title'] = tHelper.TrackName
        song['artist'] = tHelper.Artists
        song['album'] = tHelper.AlbumName
        song['tracknumber'] = str(tHelper.TrackNumber)
        song['date'] = str(tHelper.TrackPublishTime)
        song.save()    
    format = audio.split('.')[-1].lower()
    if format == 'm4a':
        # Process m4a files: Apple’s MP4 (aka M4A, M4B, M4P)
        song = easymp4.EasyMP4(audio)
        write_keys(song)
        if exists(cover):
            song = MP4(audio)
            # Write cover image
            song['covr'] = [MP4Cover(open(cover, 'rb').read())]
            song.save()
    elif format == 'mp3':
        # Process mp3 files: MPEG audio stream information and tags
        song = EasyMP3(audio)
        write_keys(song)
        if exists(cover):
            song = ID3(audio)
            # Write cover image
            song.add(APIC(encoding=3, mime='image/jpeg', type=3,
                            desc='Cover', data=open(cover, 'rb').read()))
            song.save()
    elif format == 'flac':
        # Process FLAC files:Free Lossless Audio Codec
        song = FLAC(audio)
        write_keys(song)
        if exists(cover):
            pic = Picture()
            pic.data = open(cover, 'rb').read()
            pic.mime = 'image/jpeg'
            song.add_picture(pic)
            song.save()
    elif format == 'ogg':
        # Process OGG files:Ogg Encapsulation Format
        song = OggVorbis(audio)
        write_keys(song)
        if exists(cover):
            pic = Picture()
            pic.data = open(cover, 'rb').read()
            pic.mime = 'image/jpeg'
            song["metadata_block_picture"] = [base64.b64encode(pic.write()).decode('ascii')]
            song.save()
    return True

total_queued = 0
total_progress = 0
def download(url,dest,account=False):
    global total_progress
    # Downloads generic content
    response = GetCurrentSession().get(url,stream=True)                        
    length = int(response.headers.get('content-length'))
    with open(dest,'wb') as f:
        for chunk in response.iter_content(1024 * 2 ** 10):
            if account:
                total_progress += len(chunk) / length
            f.write(chunk) # write every 1MB read            
    return dest

def executor_loop():
    def execute(task : NETrackDownloadTask):
        # Downloding source audio
        dest_src = download(task.resource.url,join(task.resource.dest,task.song.SanitizedTitle+'.'+task.resource_info['type']),account=True)
        # Downloading cover
        dest_cvr = download(task.cover.url,join(task.cover.dest,'%s.jpg' % task.cover.id))
        # Downloading & Parsing lyrics
        dest_lrc = join(task.lyrics.dest,task.song.SanitizedTitle + '.lrc')
        lrc    = LrcParser()
        dLyrics = track.GetTrackLyrics(task.lyrics.id)
        for k in set(dLyrics.keys()).intersection({'lrc','tlyric','romalrc'}):
            lrc.LoadLrc(dLyrics[k]['lyric'])                           
        open(dest_lrc,'w',encoding='utf-8').write(lrc.DumpLyrics())
        # Tagging the audio
        tag(task.song,dest_src,dest_cvr)
        # Cleaning up
        remove(dest_cvr)
        # Assigns the task as finished
        logger.debug('下载完成：%s' % (task.song.Title))
        task_queue.task_done()
    with ThreadPoolExecutor(max_workers=max_workers) as executor:        
        while True:
            task = task_queue.get()            
            executor.submit(execute,task)

def __main__():
    args = parse_args()
    if args.phone and args.password:        
        login.LoginViaCellphone(args.phone,args.password)
        logger.info('使用账号：%s (VIP %s)' % (
            GetCurrentSession().login_info['content']['profile']['nickname'],
            GetCurrentSession().login_info['content']['profile']['vipType'])
        )
    eThread = Thread(target=executor_loop)
    eThread.setDaemon(True)
    eThread.start()
    # starts execution thread
    total_queued = args.func(args)
    # now wait until all tasks are done...report some progress maybe?
    while task_queue.unfinished_tasks != 0:
        sys.stderr.write('[STAT] %.2f%% (%.0f/%d)\n' % (total_progress * 100 / total_queued,total_progress,total_queued))
        sleep(1)
    sys.stderr.write('[STAT] %.2f%% (%.0f/%d)\n' % (total_progress * 100 / total_queued,total_progress,total_queued))
    logger.info('下载完成')        
    return 0

if __name__ == '__main__':
    logger = getLogger()
    basicConfig(level='INFO',format='[%(levelname)s] %(message)s')    
    if gooey_installed:
        Gooey(              
            program_name='PyNCM Gooey GUI',
            progress_regex=r"\((?P<curr>(\d{1,3}))\/(?P<total>(\d{1,3}))\)",
            hide_progress_msg=True,
            progress_expr="curr / total * 100",
            timing_options = {
                'show_time_remaining':True,
                'hide_time_remaining_on_complete':True,
            },
            menu=[{'name':'About','items':[{
                'type': 'AboutDialog',
                'menuTitle': 'About',
                'name': 'PyNCM',
                'description': __desc__,
                'version': __version__,
                'website': 'https://github.com/greats3an/pyncm'
            }]}]
        )(__main__)()
    else:
        sys.exit(__main__())