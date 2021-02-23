'''Helper class to help work with audio / lyrics files'''
import shutil
import json
import time
import os
import sys
import logging
import base64
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import EasyMP3
from mutagen import easymp4
from mutagen.mp4 import MP4, MP4Cover
from mutagen.oggvorbis import OggVorbis
from . import LrcParser,Downloader, PoolWorker
from .. import GetCurrentSession
from .. import apis as NCM

truncate_length = 64
logger = logging.getLogger('NCMHelper')

def TrackHelperProperty(default=None):
    def preWrapper(func):
        @property
        def wrapper(*a,**k):
            try:
                return func(*a,**k)
            except:
                logger.warn('Error while getting track attribute %s,using fallback value %s' % (func.__name__,default))
                return default
        return wrapper
    return preWrapper

class TrackHelper():
    '''Helper class for handling generic track objects'''

    def __init__(self, track_dict) -> None:
        self.track = track_dict

    @TrackHelperProperty()
    def TrackPublishTime(self):
        '''The publish year of the track'''
        epoch = self.track['publishTime'] / 1000 # stored as unix timestamp though only the year was ever useful
        return time.gmtime(epoch).tm_year

    @TrackHelperProperty()
    def TrackNumber(self):
        '''The # of the track'''
        return self.track['no']

    @TrackHelperProperty(default='Unknown')
    def TrackName(self):
        '''The name of the track'''
        assert self.track['name'] != None
        return self.track['name']

    @TrackHelperProperty(default='Unknown')
    def AlbumName(self):
        '''The name of the album'''
        if self.track['al']['id']:
            return self.track['al']['name']
        else:
            return self.track['pc']['alb']

    @TrackHelperProperty(default='https://p1.music.126.net/UeTuwE7pvjBpypWLudqukA==/3132508627578625.jpg')
    def AlbumCover(self):
        '''The cover of the track's album'''
        al = self.track['al'] if 'al' in self.track.keys() else self.track['album']
        if al['id']:
            return al['picUrl']
        else:        
            return 'https://music.163.com/api/img/blur/' + self.track['pc']['cid'] 
            # source:PC version's core.js

    @TrackHelperProperty(default=['Various Artists'])
    def Artists(self):
        '''All the artists' names as a list'''
        ar = self.track['ar'] if 'ar' in self.track.keys() else self.track['artists']
        ret = [_ar['name'] for _ar in ar ]
        if not ret.count(None):
            return ret
        else:
            return [self.track['pc']['ar']] # for NCM cloud-drive stored audio

    @TrackHelperProperty()
    def Title(self):
        '''A formatted title for this song'''
        return f'{",".join(self.Artists)} - {self.TrackName}'
    _illegal_chars = set('\x00\\/:*?"<>|')
    @TrackHelperProperty()
    def SanitizedTitle(self):
        '''Sanitized title for FS compatibility; Limits max length to 200 chars,and substitutes illegal chars with their full-width counterparts'''
        def _T(s,l=100):
            return ''.join([c if not c in self._illegal_chars else chr(ord(c)+0xFEE0) for c in s])[:l]
        return f'{_T(",".join(self.Artists),100)} - {_T(self.TrackName,100)}'
class NcmHelper():
    '''Helper class to manage & queue downloads

            temp        :       Tempoary folder to stroe downloads
            output      :       Output folder to store music
            merge_only  :       If only find download file in the temp folder,then merge them without downloading
                                Applies to MutilWrapper ones
            pool_size   :       Cocurrent download worker count
            buffer_size :       Size of iter_content(chunk_size)'s chunk_size
            logger      :       For logging.Uses simple_logger from ncm.strings,leave empty for not logging    
    '''

    def __init__(self, temp='temp', output='output', merge_only=False, pool_size=4, buffer_size=256, reporter=sys.stdout):
        self.DL = Downloader(session=GetCurrentSession(), pool_size=pool_size, buffer_size=buffer_size)
        # Initalization of other classes
        self.temp, self.output, self.merge_only = temp, output, merge_only
        self.pool_size = pool_size
        self.reporter = reporter

    def parse_quality(self,quality):        
        return {'standard':96000,'high':320000,'lossless':3200000}[quality.lower()]

    def ReportStatus(self, title, done, total):
        precentage = str(int(done * 100 / total)).center(3,' ') if total else '--'
        self.reporter(
            f'{title} | {precentage}% | {done} | {total}{" " * 30}\r')
        # Trims white space

    def ShowDownloadStatus(self):
        '''
            Shows downloader info,also returns the content
        '''
        qsize, unfinished, downloading = len(
            self.DL.workers), self.DL.task_queue.unfinished_tasks, 0
        stresses = []
        for status, id, xfered, length in self.DL.reports():
            precentage = str(int(xfered * 100 / length)
                             ).center(3, ' ') if length else '--'
            if not status == 0xFF:
                downloading += 1
            stresses.append(f'{precentage}%')
        self.ReportStatus(
            f'Downloading - Progress : {" | ".join(stresses)} |  Queue stress', self.DL.task_queue.qsize(), unfinished)
        time.sleep(1)

    def GenerateDownloadPath(self, id='', filename='', folder=''):
        '''
            Generates output path with its leaf folders and such.Similar to mktree

            Specify folder to change the root folder somewhere else
        '''
        folder = os.path.join(folder, str(
            id)) if folder else os.path.join(self.temp, str(id))
        result = os.path.join(folder, filename)
        path = os.path.split(result)
        if path[0]:
            if not os.path.exists(path[0]):
                os.makedirs(path[0])
        # Make the folder tree
        return result

    def QueueDownload(self, url, path):
        '''
            Queue a download
        '''
        if not (url and path):
            return
        self.DL.append(url, path)
        logger.debug('Queued download ...%s -> ...%s' %
                     (url[-truncate_length:], path[-truncate_length:]))

    def QueueDownloadTrackAudio(self, id, quality='lossless', folder=''):
        '''
            This will queue to download only the song's audio file (named 'audio.*') to a certain directory.
        '''
        info = NCM.track.GetTrackAudio(song_ids=id, bitrate=self.parse_quality(quality))
        if not info['code'] == 200:
            return
        filename = '{}.{}'.format('audio', info['data'][0]['type'])
        target = self.GenerateDownloadPath(filename=filename, folder=folder)
        url = info['data'][0]['url']
        self.QueueDownload(url, target)
        return target

    def QueueDownloadTrackInfo(self, id, folder=''):
        '''
            This will write the song's trackdata into JSON (named track.json) and queue to download cover (named cover.jpg) to a certain directory.
        '''
        track = NCM.track.GetTrackDetail(id)['songs'][0]
        self.QueueDownload(track['al']['picUrl'], self.GenerateDownloadPath(
            filename='cover.jpg', folder=folder))
        # Queue to download cover image
        target = self.GenerateDownloadPath(
            filename='track.json', folder=folder)
        open(target, mode='w', encoding='utf-8').write(json.dumps(track))
        # Writes trackdata to JSON file
        return True

    def QueueDownloadAllTracksInAlbum(self, id, quality='lossless', folder=''):
        '''
            This will get every song's ID inside the album resovled

            Note that extra info will be stored inside the JSON that the api sent
        '''
        info = NCM.album.GetAlbumInfo(id)
        root = folder
        # Go through every track inside the JSON
        done, total = 0, len(info['songs'])
        trackIds = [song['id'] for song in info['songs']]
        tracks = NCM.track.GetTrackDetail(trackIds)['songs']
        trackAudios = NCM.track.GetTrackAudio(trackIds, bitrate=self.parse_quality(quality))['data']
        
        tracks = sorted(tracks,key=lambda song:song['id'])
        trackAudios = sorted(trackAudios,key=lambda song:song['id'])        
        
        for i in range(0,len(tracks)):
            # Since the begging of 2020,NE no longer put complete playlist in the `tracks` key
            track,trackAudio = tracks[i],trackAudios[i]
            # Generates track header,and saves them\
            trackId = track['id']
            tHelper = TrackHelper(track)
            track_root = self.GenerateDownloadPath(id=trackId, folder=root)
            open(self.GenerateDownloadPath(filename='track.json', folder=track_root),
                 mode='w', encoding='utf-8').write(json.dumps(track))
            # Download lyrics
            self.DownloadAndFormatLyrics(trackId, folder=track_root)
            # Queue to download audio and cover image
            self.QueueDownload(trackAudio['url'], self.GenerateDownloadPath(
                filename=f'audio.{trackAudio["type"]}', folder=track_root))
            self.QueueDownload(tHelper.AlbumCover, self.GenerateDownloadPath(
                filename='cover.jpg', folder=track_root))
            done += 1
            self.ReportStatus('Queueing download', done, total)
        return info

    def QueueDownloadAllTracksInPlaylist(self, id, quality='lossless', folder=''):
        '''
            This will try and get all songs' ID and such in the playlist,then try to download them.

            The strcuture is very similar to the album one,but with some minor twists
        '''
        info = NCM.playlist.GetPlaylistInfo(id)
        try:
            name, creator = info['playlist']['name'], info['playlist']['creator']['nickname']
        except Exception as e:
            raise Exception('Failed to fetch Playlist info:%s' % e)
        root = folder
        # Go through every track inside the JSON
        trackIds = [tid['id'] for tid in info['playlist']['trackIds']]

        done, total = 0, len(trackIds)

        tracks = NCM.track.GetTrackDetail(trackIds)['songs']
        trackAudios = NCM.track.GetTrackAudio(trackIds, bitrate=self.parse_quality(quality))['data']

        tracks = sorted(tracks,key=lambda song:song['id'])
        trackAudios = sorted(trackAudios,key=lambda song:song['id'])        

        for i in range(0,len(tracks)):
            # Since the begging of 2020,NE no longer put complete playlist in the `tracks` key
            track,trackAudio = tracks[i],trackAudios[i]
            trackId = track['id']
            tHelper = TrackHelper(track)
            # Generates track header,and saves them
            track_root = self.GenerateDownloadPath(id=trackId, folder=root)
            open(self.GenerateDownloadPath(filename='track.json', folder=track_root),
                 mode='w', encoding='utf-8').write(json.dumps(track))
            # Download lyrics
            self.DownloadAndFormatLyrics(trackId, folder=track_root)
            # Queue to download audio and cover image        
            self.QueueDownload(trackAudio['url'], self.GenerateDownloadPath(
                filename=f'audio.{trackAudio["type"]}', folder=track_root))
            self.QueueDownload(tHelper.AlbumCover, self.GenerateDownloadPath(
                filename='cover.jpg', folder=track_root))
            done += 1
            self.ReportStatus('Queueing download', done, total)
        return info

    def DownloadTrackLyrics(self, id, folder=''):
        '''
            This will only write the song's lyrics into JSON (named lyrics.json) to a certain directory.
        '''
        lyrics = NCM.track.GetTrackLyrics(id)
        target = self.GenerateDownloadPath(
            filename='lyrics.json', folder=folder)
        open(target, mode='w', encoding='utf-8').write(json.dumps(lyrics))
        # Writes lyrics to JSON file
        return lyrics

    def FormatLyrics(self, folder, export=''):
        '''
            Coverts a dictionary with timestamps as keys and lyrics as items into LRC lyrics
        '''
        export = export if export else self.output        
        lyrics = json.loads(open(self.GenerateDownloadPath(filename='lyrics.json',folder=folder), encoding='utf-8').read())  
        track  = json.loads(open(self.GenerateDownloadPath(filename='track.json', folder=folder), encoding='utf-8').read())
        rawlrcs= [lyrics[k]['lyric'] for k in set(lyrics.keys()).intersection({'lrc','tlyric','romalrc'}) if 'lyric' in lyrics[k].keys()]
        lrc    = LrcParser()
        for rawlrc in rawlrcs:
            this = LrcParser(rawlrc)
            lrc.UpdateLyrics(this.lyrics.items(),timestamp_function=lambda l:l[0],lyrics_function=lambda l:[v[1] for v in l[1]])            
        # Writing some metadata
        users = '/'.join([lyrics[k]['nickname'] for k in set(lyrics.keys()).intersection({'transUser','lyricUser'})])
        tHelper = TrackHelper(track)        
        # -- METADATA --
        lrc.LRCAuthor = users        
        lrc.Album = tHelper.AlbumName
        if tHelper.Artists:lrc.Artist = ','.join(tHelper.Artists)
        lrc.Title = tHelper.Title
        lrc.Program = 'PyNCM' # leaving a mark hehe
        # -- METADATA --

        # Saving the lyrics        
        
        path = self.GenerateDownloadPath(filename=tHelper.SanitizedTitle + '.lrc', folder=export)
        open(path, mode='w', encoding='utf-8').write(lrc.DumpLyrics())
        logger.debug('Downloaded lyrics ...%s' % path[-truncate_length:])
        return True

    def TagTrack(self, folder, export=''):
        '''
            'Tag' a song's trackdata with the infomation given in folder

            Call once all download tasks is finished

            Suppports MP3,M4A(ALAC/MP4),FLAC
        '''

        export = export if export else self.output
        folder = str(folder)
        audio = [f for f in os.listdir(folder) if f.split('.')[-1].lower() in ['mp3', 'm4a', 'flac','ogg']]
        if not audio:
            logger.error('Supported audio file for %s is missing,Cannot continue formatting!' % folder)
            return     
        audio = audio[-1]
        audio = self.GenerateDownloadPath(filename=audio, folder=folder)
        format = audio.split('.')[-1].lower()
        # Locate audio file,uses last match
        track = self.GenerateDownloadPath(filename='track.json', folder=folder)
        # Locate track file
        cover = self.GenerateDownloadPath(filename='cover.jpg', folder=folder)
        # Locate cover image

        track = json.loads(open(track, encoding='utf-8').read())
        tHelper = TrackHelper(track)

        def write_keys(song):
            # Write trackdatas
            song['title'] = tHelper.TrackName
            song['artist'] = tHelper.Artists if tHelper.Artists else 'Various Artists'
            song['album'] = tHelper.AlbumName if tHelper.AlbumName else 'Unknown'
            song['tracknumber'] = str(tHelper.TrackNumber)
            song['date'] = str(tHelper.TrackPublishTime)
            song.save()

        if format == 'm4a':
            # Process m4a files: Apple’s MP4 (aka M4A, M4B, M4P)
            song = easymp4.EasyMP4(audio)
            write_keys(song)
            if os.path.exists(cover):
                song = MP4(audio)
                # Write cover image
                song['covr'] = [MP4Cover(open(cover, 'rb').read())]
                song.save()
        elif format == 'mp3':
            # Process mp3 files: MPEG audio stream information and tags
            song = EasyMP3(audio)
            write_keys(song)
            if os.path.exists(cover):
                song = ID3(audio)
                # Write cover image
                song.add(APIC(encoding=3, mime='image/jpeg', type=3,
                              desc='Cover', data=open(cover, 'rb').read()))
                song.save()
        elif format == 'flac':
            # Process FLAC files:Free Lossless Audio Codec
            song = FLAC(audio)
            write_keys(song)
            if os.path.exists(cover):
                pic = Picture()
                pic.data = open(cover, 'rb').read()
                pic.mime = 'image/jpeg'
                song.add_picture(pic)
                song.save()
        elif format == 'ogg':
            # Process OGG files:Ogg Encapsulation Format
            song = OggVorbis(audio)
            write_keys(song)
            if os.path.exists(cover):
                pic = Picture()
                pic.data = open(cover, 'rb').read()
                pic.mime = 'image/jpeg'
                song["metadata_block_picture"] = [base64.b64encode(pic.write()).decode('ascii')]
                song.save()
        # Rename & move file
        savename = tHelper.SanitizedTitle + '.' + format
        try:
            path = self.GenerateDownloadPath(filename=savename, folder=export)
            shutil.copy(audio, path)
            logger.debug('Exported audio to path %s' % path[-truncate_length:])
            return path
        except Exception as e:
            raise Exception('While copying audio file:%s' % e)

    def DownloadTrackAudio(self, id, quality='lossless', folder=''):
        '''
            Download Audio,and wait for it to finish
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        self.QueueDownloadTrackAudio(id, quality, folder)
        self.DL.wait(func=self.ShowDownloadStatus)
        logger.debug('Downloaded audio file for id %s' % id)
        return True

    def DownloadTrackInfo(self, id, folder=''):
        '''
            Download info,and wait for it to finish
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        self.QueueDownloadTrackInfo(id, folder)
        self.DL.wait(func=self.ShowDownloadStatus)
        logger.debug('Downloaded audio track for id %s' % id)
        return True

    def DownloadAndFormatLyrics(self, id, folder=''):
        '''
            Both download,and format the lyrics
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        self.DownloadTrackLyrics(id, folder)
        self.FormatLyrics(folder)
        return True

    def DownloadAll(self, id, quality='lossless', folder=''):
        '''
            Download everything we need,then wait for download to finish.
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        # Download track and cover.Note that cover is downloaded asynchronously
        self.QueueDownloadTrackInfo(id, folder)
        # Download lyrics
        self.DownloadAndFormatLyrics(id)
        # Download song.Not that audio file is downloaded asynchronously
        self.QueueDownloadTrackAudio(id, quality, folder)
        self.DL.wait(func=self.ShowDownloadStatus)
        logger.debug('Downloaded everything for id %s' % id)
        return True

    def DownloadAllAndMerge(self, id, quality='lossless', folder=''):
        '''
            This will merge the infomation once download is finished
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        self.DownloadAll(id, quality, folder)
        self.DownloadAndFormatLyrics(id, folder)
        self.TagTrack(folder)
        return True

    def Login(self, username, password):
        return NCM.login.LoginViaCellphone(username, password)

    def MutilWrapper(self, queue_func):
        '''
            Wraps around a queue method.Once downloaded,

            perform the merging proceess for each and every sub folder
        '''
        def wrapper(id, quality='lossless', folder=None, merge_only=False):
            if not folder:
                folder = self.GenerateDownloadPath(id=id, folder=folder)
            if not self.merge_only:
                logger.info('Queuing download for specified resources...')
                queue_func(id, quality, folder)
                self.DL.wait(func=self.ShowDownloadStatus)
                # Queue then wait
            processed = 0

            def tag(subfolder):
                self.FormatLyrics(subfolder)
                self.TagTrack(subfolder)
            # Start merging every subfolder via threadpool,where it's a mutation of the Downloader
            pool = Downloader(worker=PoolWorker, pool_size=self.pool_size)
            for sub in os.listdir(folder):
                pool.append(tag, os.path.join(folder, sub))
            def wait():
                self.ReportStatus('Tagging audio', len(os.listdir(folder)) - pool.task_queue.unfinished_tasks, len(os.listdir(folder)))
                time.sleep(1)
            pool.wait(func=wait)
        return wrapper

    def DownloadAllTracksInPlaylistAndMerge(self, id, quality='lossless', folder=None, merge_only=False):
        '''
            Downloads all songs in a playlist into selected folder

                id          :       Song ID
                quality     :       Song Quality
                folder      :       Output folder
                merge_only  :       Merge by id from 'folder',Only use this if you 
                                    Have finished downloading first
        '''
        return self.MutilWrapper(self.QueueDownloadAllTracksInPlaylist)(id, quality, folder, merge_only)

    def DownloadAllTracksInAlbumAndMerge(self, id, quality='lossless', folder=None, merge_only=False):
        '''
            Downloads all albums in a playlist into selected folder

                id          :       Song ID
                quality     :       Song Quality
                folder      :       Output folder
                merge_only  :       Merge by id from 'folder',Only use this if you 
                                    Have finished downloading first
        '''
        return self.MutilWrapper(self.QueueDownloadAllTracksInAlbum)(id, quality, folder, merge_only)

