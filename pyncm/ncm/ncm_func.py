'''
# Netease Cloud Music Func
For direct disk I/O Access and ease-of-use for downloading,tagging music of NE
'''
import argparse
import re
import shutil
import json
import time
import os
import sys
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import EasyMP3
from mutagen import easymp4
from mutagen.mp4 import MP4, MP4Cover
from ..utils.downloader import Downloader, DownloadWorker, PoolWorker
from .ncm_core import NeteaseCloudMusic
from . import Depercated, logger, session
import time

def TrackHelperProperty(func):
    @property
    def wrapper(*a,**k):
        try:
            return func(*a,**k)
        except Exception as e:
            logger.warn('Error while getting track attribute %s:%s' % (func.__name__,e))
            return None        
    return wrapper
class TrackHelper():
    def __init__(self, track_dict) -> None:
        self.track = track_dict

    @property
    def TrackPublishTime(self):
        '''The publish time of the track'''
        epoch = self.track['publishTime'] / 1000 # js timestamps are in milliseconds.
                                                 # converting to unix timestamps (in seconds),we need to divide by 1000
        return time.gmtime(epoch)

    @property
    def TrackNumber(self):
        '''The # of the track'''
        return self.track['no']

    @property
    def TrackName(self):
        '''The name of the track'''
        return self.track['name']

    @property
    def AlbumName(self):
        '''The name of the album'''
        return self.track['al']['name']

    @property
    def AlbumCover(self):
        '''The cover of the track's album'''
        return self.track['al']['picUrl']

    @property
    def Artists(self):
        '''All the artists' names as a list'''
        return [ar['name'] for ar in self.track['ar']]


class NCMFunctions():
    '''
        Functions using ncm_core.py,simplfied to download songs easily

            temp        :       Tempoary folder to stroe downloads
            output      :       Output folder to store music
            merge_only  :       If only find download file in the temp folder,then merge them without downloading
                                Applies to MutilWrapper ones
            pool_size   :       Cocurrent download worker count
            buffer_size :       Size of iter_content(chunk_size)'s chunk_size
            logger      :       For logging.Uses simple_logger from ncm.strings,leave empty for not logging
            random_keys     :       Whether uses random 2nd AES key or the constant 'mos9527ItoooItop' and its encypted RSA string
        Functions inside are well described,read them for more info.
    '''

    def __init__(self, temp='temp', output='output', merge_only=False, pool_size=4, buffer_size=256, random_keys=False, reporter=sys.stdout):
        self.NCM = NeteaseCloudMusic(random_keys)
        self.DL = Downloader(
            session=session, pool_size=pool_size, buffer_size=buffer_size)
        # Initalization of other classes
        self.temp, self.output, self.merge_only = temp, output, merge_only
        self.pool_size = pool_size
        self.reporter = reporter

    def ReportStatus(self, title, done, total):
        precentage = str(int(done * 100 / total)).center(3,
                                                         ' ') if total else '--'
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
        def normalize(s):
            mapping = {
                '\\': ' ',
                '/': '',
                ':': '：',
                '*': '·',
                '?': '？',
                '"': '”',
                '<': '《',
                '>': '》',
                '|': '、'
            }
            for k, v in mapping.items():
                s = s.replace(k, v)
            return s
        filename = normalize(filename)
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
                     (url[-16:], path[-16:]))

    def QueueDownloadTrackAudio(self, id, quality='lossless', folder=''):
        '''
            This will queue to download only the song's audio file (named 'audio.*') to a certain directory.
        '''
        info = self.NCM.GetTrackAudioInfo(song_ids=id, quality=quality)
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
        track = self.NCM.GetTrackDetail(id)['songs'][0]
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
        info = self.NCM.GetAlbumInfo(id)
        try:
            name, creator = info['title'], info['author']
        except Exception as e:
            raise Exception('Failed to fetch Album info:%s' % e)
        root = folder
        # Go through every track inside the JSON
        done, total = 0, len(info['songlist'])
        trackIds = [song['id'] for song in info['songlist']]
        tracks = self.NCM.GetTrackDetail(trackIds)
        trackAudios = self.NCM.GetTrackAudioInfo(trackIds, quality=quality)

        for trackNo in range(0, len(tracks['songs'])):
            track = tracks['songs'][trackNo]
            trackAudio = trackAudios['data'][trackNo]
            trackId = track['id']
            # Generates track header,and saves them
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
        info = self.NCM.GetPlaylistInfo(id)
        try:
            name, creator = info['playlist']['name'], info['playlist']['creator']['nickname']
        except Exception as e:
            raise Exception('Failed to fetch Playlist info:%s' % e)
        root = folder
        # Go through every track inside the JSON
        trackIds = [tid['id'] for tid in info['playlist']['trackIds']]

        done, total = 0, len(trackIds)
        tracks = self.NCM.GetTrackDetail(trackIds)
        trackAudios = self.NCM.GetTrackAudioInfo(trackIds, quality=quality)
        for trackNo in range(0, len(tracks['songs'])):
            # Since the begging of 2020,NE no longer put complete playlist in the `tracks` key
            track = tracks['songs'][trackNo]
            trackAudio = trackAudios['data'][trackNo]
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
        lyrics = self.NCM.GetTrackLyrics(id)
        target = self.GenerateDownloadPath(
            filename='lyrics.json', folder=folder)
        open(target, mode='w', encoding='utf-8').write(json.dumps(lyrics))
        # Writes lyrics to JSON file
        return lyrics

    def LoadLyrics(self, folder):
        '''
            Converts the lyrics JSON format into a dictionary
        '''
        lyrics = self.GenerateDownloadPath(
            filename='lyrics.json', folder=folder)
        # Locate lyric file
        if not os.path.exists(lyrics):
            logger.error('Missing lyrics.json,LRC will not be parsed')
            return {}
        lyrics = json.loads(open(lyrics, encoding='utf-8').read())
        # Load lyrics into json file
        lrc_lists = [lyrics[lrc]['lyric'] for lrc in lyrics.keys(
        ) if lrc in ['lrc', 'tlyric'] and 'lyric' in lyrics[lrc].keys()]
        # List all lyrics.Translation is optional
        timestamp_regex = r"(?:\[)(\d{2,}:\d{2,}.\d{2,})(?:\])(.*)"
        lyrics_combined = {}
        for lrc_ in lrc_lists:
            if not lrc_:
                continue
            lrc_lrc = lrc_.split('\n')
            # Split lyrics into an array
            for lrc in lrc_lrc:
                result = re.search(timestamp_regex, lrc)
                if not result:
                    continue
                timestamp, content = result.group(1), result.group(2)
                if not timestamp in lyrics_combined.keys():
                    lyrics_combined[timestamp] = []
                lyrics_combined[timestamp].append(content)

        return lyrics_combined

    def FormatLyrics(self, folder, export=''):
        '''
            Coverts a dictionary with timestamps as keys and lyrics as items into LRC lyrics
        '''
        export = export if export else self.output
        lyrics = self.LoadLyrics(folder)
        if not lyrics:
            return
        track = self.GenerateDownloadPath(filename='track.json', folder=folder)
        # Locate track file
        if not os.path.exists(track):
            logger.warn('Missing track.json,will skip track info parsing')
            track = {
                'name': 'undefined',
                'album': 'undefined',
                'author': 'undefined'
            }
        else:
            track = json.loads(open(track, encoding='utf-8').read())
        # Load JSON for future purposes
        tHelper = TrackHelper(track)
        lrc = f"""[ti:{tHelper.TrackName}]\n[al:{tHelper.AlbumName}]\n[au:{','.join(tHelper.Artists)}]\n[re:PyNCM]\n"""

        for timestamp in lyrics.keys():
            newline = '[%s]' % timestamp
            newline += '\t'.join(lyrics[timestamp])
            lrc += '\n' + newline
        path = self.GenerateDownloadPath(
            filename='{0} - {1}.{2}'.format(tHelper.TrackName, ' - '.join(tHelper.Artists), 'lrc'), folder=export)
        open(path, mode='w', encoding='utf-8').write(lrc)
        logger.debug('Downloaded lyrics ...%s' % path[-16:])
        return lrc

    def TagTrack(self, folder, export=''):
        '''
            'Tag' a song's trackdata with the infomation given in folder

            Call once all download tasks is finished

            Suppports MP3,M4A(ALAC/MP4),FLAC
        '''
        export = export if export else self.output
        folder = str(folder)
        audio = [f for f in os.listdir(folder) if f.split(
            '.')[-1] in ['mp3', 'm4a', 'flac']]
        if not audio:
            return
        audio = audio[-1]
        audio = self.GenerateDownloadPath(filename=audio, folder=folder)
        format = audio.split('.')[-1]
        # Locate audio file,uses last match
        track = self.GenerateDownloadPath(filename='track.json', folder=folder)
        # Locate track file
        cover = self.GenerateDownloadPath(filename='cover.jpg', folder=folder)
        # Locate cover image

        if not audio:
            logger.error(
                'audio.m4a / audio.mp3 / audio.flac is missing,Cannot continue formatting!')
            return

        track = json.loads(open(track, encoding='utf-8').read())
        tHelper = TrackHelper(track)

        def write_keys(song):
            # Write trackdatas
            song['title'] = tHelper.TrackName
            song['artist'] = tHelper.Artists
            song['album'] = tHelper.AlbumName
            song['tracknumber'] = str(tHelper.TrackNumber)
            song['date'] = str(tHelper.TrackPublishTime.tm_year)
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

        # Rename & move file
        savename = '{1} - {0}.{2}'.format(tHelper.TrackName,
                                          ','.join(tHelper.Artists), format)
        try:
            path = self.GenerateDownloadPath(filename=savename, folder=export)
            shutil.copy(audio, path)
            logger.debug('Exported audio to path %s' % path[-16:])
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
        '''
        Login method,equals to ncm_core.UpdateLoginInfo
        '''
        return self.NCM.UpdateLoginInfo(username, password)

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
            pool = Downloader(worker=PoolWorker, pool_size=8)
            for sub in os.listdir(folder):
                pool.append(tag, os.path.join(folder, sub))

            def wait():
                self.ReportStatus('Tagging audio', len(os.listdir(
                    folder)) - pool.task_queue.unfinished_tasks, len(os.listdir(folder)))
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
