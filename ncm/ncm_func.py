'''
@Author: greats3an
@Date: 2020-01-24 11:32:51
@LastEditors  : greats3an
@LastEditTime : 2020-02-11 17:00:23
@Site: mos9527.tooo.top
@Description: Functions utilizing self.NCM_core.py
'''
import argparse,re,shutil,json,time,os,sys
from colorama import Cursor
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import EasyMP3
from mutagen import easymp4
from mutagen.mp4 import MP4, MP4Cover

from utils.downloader import Downloader,DownloadWorker,PoolWorker
from .ncm_core import NeteaseCloudMusic
from .strings import simple_logger, strings


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
    def __init__(self,temp='temp',output='output',merge_only=False,pool_size=4,buffer_size=256,random_keys=False,logger=lambda *args,**kwargs:None):
        self.NCM = NeteaseCloudMusic(logger,random_keys)
        self.DL = Downloader(session=self.NCM.session,pool_size=pool_size,buffer_size=buffer_size)
        # Initalization of other classes
        self.temp,self.output,self.merge_only = temp,output,merge_only
        self.log = logger;self.pool_size = pool_size
    def ShowDownloadStatus(self):
        '''
            Shows downloader info
        '''
        content = self.DL.report(strings.DEBUG_DOWNLOAD_STATUS(None))
        print(content, Cursor.UP(content.count('\n') + 1))
        time.sleep(1)

    def GenerateDownloadPath(self,id='', filename='', folder=''):
        '''
            Generates output path with its leaf folders and such.Similar to mktree

            Specify folder to change the root folder somewhere else
        '''
        def normalize(s):return s.replace(':','：').replace('\n','_').replace('-','_').replace(',','，').replace('"','“').replace('\'','”').replace('/','、').replace('\\','，')
        filename = normalize(filename)
        folder = os.path.join(folder, str(id)) if folder else os.path.join(self.temp, str(id))
        result = os.path.join(folder, filename)
        path = os.path.split(result)
        if path[0]:
             if not os.path.exists(path[0]):os.makedirs(path[0])
        # Make the folder tree
        return result
    def QueueDownload(self,url, path):
        '''
            Queue a download
        '''
        self.DL.append(url, path)
        self.log(url, path, format=strings.INFO_QUEUED_DOWNLOAD)

    def QueueDownloadSongAudio(self,id, quality='lossless', folder=''):
        '''
            This will queue to download only the song's audio file (named 'audio.*') to a certain directory.
        '''
        info = self.NCM.GetSongInfo(song_id=id, quality=quality)
        if not info['code'] == 200:return
        filename = '{}.{}'.format('audio', info['data'][0]['type'])
        target = self.GenerateDownloadPath(filename=filename, folder=folder)
        url = info['data'][0]['url']
        self.QueueDownload(url, target)
        return target

    def QueueDownloadSongInfo(self,id, folder=''):
        '''
            This will write the song's metadata into JSON (named meta.json) and queue to download cover (named cover.jpg) to a certain directory.
        '''
        info = self.NCM.GetExtraSongInfo(id)
        self.QueueDownload(info['cover'], self.GenerateDownloadPath(
            filename='cover.jpg', folder=folder))
        # Queue to download cover image
        target = self.GenerateDownloadPath(filename='meta.json', folder=folder)
        open(target, mode='w', encoding='utf-8').write(json.dumps(info))
        # Writes metadata to JSON file

    def QueueDownloadAllSongsInAlbum(self,id, quality='lossless', folder=''):
        '''
            This will get every song's ID inside the album resovled

            Note that extra info will be stored inside the JSON that the api sent
        '''
        info = self.NCM.GetAlbumInfo(id)
        try:
            name, creator = info['title'], info['author']
            self.log(name, creator, format=strings.INFO_FETCHED_ALBUM_WITH_TOKEN)
        except Exception as e:
            self.log(e, format=strings.ERROR_INVALID_OPERATION)
        root = folder
        # Go through every track inside the JSON
        for track in info['songlist']:
            meta = {
                "title": track['name'],
                "cover": track['album']['picUrl'],
                "author": ' - '.join([a['name'] for a in track['artists']]),
                "album": track['album']['name'],
                "album_id": track['album']['id'],
                "artist_id": ' - '.join([str(a['id']) for a in track['artists']])
            }
            # Generates meta header,and saves them
            track_id = track['id']
            track_root = self.GenerateDownloadPath(id=track_id, folder=root)
            open(self.GenerateDownloadPath(filename='meta.json', folder=track_root),
                mode='w', encoding='utf-8').write(json.dumps(meta))
            # Download lyrics
            self.DownloadAndFormatLyrics(track_id, folder=track_root)
            # Queue to download audio and cover image
            self.QueueDownloadSongAudio(track_id, quality, track_root)
            self.QueueDownload(meta['cover'], self.GenerateDownloadPath(
                filename='cover.jpg', folder=track_root))

    def QueueDownloadAllSongsInPlaylist(self,id, quality='lossless', folder=''):
        '''
            This will try and get all songs' ID and such in the playlist,then try to download them.

            The strcuture is very similar to the album one,but with some minor twists
        '''
        info = self.NCM.GetPlaylistInfo(id)
        try:
            name, creator = info['playlist']['name'], info['playlist']['creator']['nickname']
            self.log(name, creator, format=strings.INFO_FETCHED_PLAYLIST_WITH_TOKEN)
        except Exception as e:
            self.log(e, format=strings.ERROR_INVALID_OPERATION)
        root = folder
        # Go through every track inside the JSON
        for track in info['playlist']['tracks']:
            meta = {
                "title": track['name'],
                "cover": track['al']['picUrl'],
                "author": ' - '.join([a['name'] for a in track['ar']]),
                "album": track['al']['name'],
                "album_id": track['al']['id'],
                "artist_id": ' - '.join([str(a['id']) for a in track['ar']])
            }
            # Generates meta header,and saves them
            track_id = track['id']
            track_root = self.GenerateDownloadPath(id=track_id, folder=root)
            open(self.GenerateDownloadPath(filename='meta.json', folder=track_root),
                mode='w', encoding='utf-8').write(json.dumps(meta))
            # Download lyrics
            self.DownloadAndFormatLyrics(track_id, folder=track_root)
            # Queue to download audio and cover image
            self.QueueDownloadSongAudio(track_id, quality, track_root)
            self.QueueDownload(meta['cover'], self.GenerateDownloadPath(
                filename='cover.jpg', folder=track_root))

    def DownloadSongLyrics(self,id, folder=''):
        '''
            This will only write the song's lyrics into JSON (named lyrics.json) to a certain directory.
        '''
        lyrics = self.NCM.GetSongLyrics(id)
        target = self.GenerateDownloadPath(filename='lyrics.json', folder=folder)
        open(target, mode='w', encoding='utf-8').write(json.dumps(lyrics))
        # Writes lyrics to JSON file

    def LoadLyrics(self,folder):
        '''
            Converts the lyrics JSON format into a dictionary
        '''
        lyrics = self.GenerateDownloadPath(filename='lyrics.json', folder=folder)
        # Locate lyric file
        if not os.path.exists(lyrics):
            self.log('lyrics.json', format=strings.ERROR_FILE_MISSING)
            return
        lyrics = json.loads(open(lyrics, encoding='utf-8').read())
        # Load lyrics into json file
        lrc_lists = [lyrics[lrc]['lyric'] for lrc in lyrics.keys() if lrc in ['lrc', 'tlyric'] and 'lyric' in lyrics[lrc].keys()]
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

    def FormatLyrics(self,folder, export=''):
        '''
            Coverts a dictionary with timestamps as keys and lyrics as items into LRC lyrics
        '''
        export = export if export else self.output
        lyrics = self.LoadLyrics(folder)
        if not lyrics:
            return
        meta = self.GenerateDownloadPath(filename='meta.json', folder=folder)
        # Locate meta file
        if not os.path.exists(meta):
            self.log('meta.json', format=strings.ERROR_FILE_MISSING)
            return
        meta = json.loads(open(meta, encoding='utf-8').read())
        # Load JSON for future purposes
        lrc = f"""[ti:{meta['title']}]
[al:{meta['album']}]
[au:{meta['author']}]
[re:Pyself.NCM]"""

        for timestamp in lyrics.keys():
            newline = '[%s]' % timestamp
            newline += '\t'.join(lyrics[timestamp])
            lrc += '\n' + newline
        path = self.GenerateDownloadPath(
            filename='{1} - {0}.{2}'.format(meta['title'], meta['author'], 'lrc'), folder=export)
        open(path, mode='w', encoding='utf-8').write(lrc)
        self.log(path, format=strings.INFO_EXPORT_COMPLETE)
        return path

    def FormatSong(self,folder, export=''):
        '''
            'Format' a song's metadata with the infomation given in folder

            Call once all download tasks is finished

            Suppports MP3,M4A(ALAC/MP4),FLAC
        '''
        export = export if export else self.output
        folder = str(folder)
        audio = [f for f in os.listdir(folder) if f.split('.')[-1] in ['mp3', 'm4a', 'flac']]
        if not audio:return
        audio = audio[-1]
        audio = self.GenerateDownloadPath(filename=audio, folder=folder)
        format = audio.split('.')[-1]
        # Locate audio file,uses last match
        meta = self.GenerateDownloadPath(filename='meta.json', folder=folder)
        # Locate meta file
        cover = self.GenerateDownloadPath(filename='cover.jpg', folder=folder)
        # Locate cover image

        if not audio:
            self.log('audio.m4a / audio.mp3 / audio.flac',
                format=strings.ERROR_FILE_MISSING)
            return
        if not os.path.exists(meta):
            self.log('meta.json', format=strings.ERROR_FILE_MISSING)
            return
        if not os.path.exists(cover):
            self.log('cover.jpg', format=strings.WARN_FILE_MISSING)


        meta = json.loads(open(meta, encoding='utf-8').read())

        def write_keys(song):
            # Write metadatas
            song['title'] = meta['title']
            song['artist'] = meta['author']
            song['album'] = meta['album']
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
        savename = '{1} - {0}.{2}'.format(meta['title'], meta['author'], format)
        try:
            path = self.GenerateDownloadPath(filename=savename, folder=export)
            shutil.copy(audio, path)
            self.log(path, format=strings.INFO_EXPORT_COMPLETE)
        except Exception as e:
            self.log(e,format=strings.ERROR_INVALID_OPERATION)
        return path

    def DownloadSongAudio(self,id, quality='lossless', folder=''):
        '''
            Download Audio,and wait for it to finish
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        quality = quality.replace('quality_', '')
        self.QueueDownloadSongAudio(id, quality, folder)
        self.DL.wait(func=self.ShowDownloadStatus)
        self.log(strings.INFO_BATCH_DOWNLOAD_COMPLETE)
        return True

    def DownloadSongInfo(self,id, folder=''):
        '''
            Download info,and wait for it to finish
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        self.QueueDownloadSongInfo(id, folder)
        self.DL.wait(func=self.ShowDownloadStatus)
        self.log(strings.INFO_BATCH_DOWNLOAD_COMPLETE)
        return True

    def DownloadAndFormatLyrics(self,id, folder=''):
        '''
            Both download,and format the lyrics
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        self.DownloadSongLyrics(id, folder)
        self.FormatLyrics(folder)
        return True

    def DownloadAllInfo(self,id, quality='lossless', folder=''):
        '''
            Download everything we need,then wait for download to finish.
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        quality = quality.replace('quality_', '')
        # Download meta and cover.Note that cover is downloaded asynchronously
        self.QueueDownloadSongInfo(id, folder)
        # Download lyrics
        self.DownloadAndFormatLyrics(id)
        # Download song.Not that audio file is downloaded asynchronously
        self.QueueDownloadSongAudio(id, quality, folder)
        self.DL.wait(func=self.ShowDownloadStatus)
        self.log(strings.INFO_BATCH_DOWNLOAD_COMPLETE)
        return True

    def DownloadAllAndMerge(self,id, quality='lossless', folder=''):
        '''
            This will merge the infomation once download is finished
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        quality = quality.replace('quality_', '')
        self.DownloadAllInfo(id, quality, folder)
        self.DownloadAndFormatLyrics(id, folder)
        self.FormatSong(folder)
        return True

    def Login(self,username, password):
        '''
        Login method,equals to ncm_core.UpdateLoginInfo
        '''
        return self.NCM.UpdateLoginInfo(username, password)

    def MutilWrapper(self,queue_func):
        '''
            Wraps around a queue method.Once downloaded,
            
            perform the merging proceess for each and every sub folder
        '''
        def wrapper(id, quality='lossless', folder=None,merge_only=False):
            if not folder:
                folder = self.GenerateDownloadPath(id=id, folder=folder)
            quality = quality.replace('quality_', '')
            if not self.merge_only:
                queue_func(id, quality, folder)
                self.DL.wait(func=self.ShowDownloadStatus)
                # Queue then wait
            self.log(strings.INFO_BATCH_DOWNLOAD_COMPLETE)
            def merge(subfolder):
                self.FormatLyrics(subfolder)
                self.FormatSong(subfolder)
            # Start merging every subfolder via threadpool,where it's a mutation of the Downloader
            pool = Downloader(worker=PoolWorker,pool_size=16)
            for sub in os.listdir(folder):
                target = os.path.join(folder, sub)
                pool.append(merge,target)
            pool.wait()
        return wrapper

    def DownloadAllSongsInPlaylistAndMerge(self,id, quality='lossless', folder=None,merge_only=False):
        return self.MutilWrapper(self.QueueDownloadAllSongsInPlaylist)(id, quality, folder,merge_only)

    def DownloadAllSongsInAlbumAndMerge(self,id, quality='lossless', folder=None,merge_only=False):
        return self.MutilWrapper(self.QueueDownloadAllSongsInAlbum)(id, quality, folder,merge_only)
