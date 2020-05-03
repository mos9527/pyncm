'''
# Netease Cloud Music Func
For direct disk I/O Access and ease-of-use for downloading,tagging music of NE
'''
import argparse,re,shutil,json,time,os,sys
from colorama import Cursor
from mutagen.flac import FLAC, Picture
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import EasyMP3
from mutagen import easymp4
from mutagen.mp4 import MP4, MP4Cover
try:
    from utils.downloader import Downloader,DownloadWorker,PoolWorker
except Exception:
    from ..utils.downloader import Downloader,DownloadWorker,PoolWorker
# If used as module..
from .ncm_core import NeteaseCloudMusic
from . import Depercated,logger,session

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
    def __init__(self,temp='temp',output='output',merge_only=False,pool_size=4,buffer_size=256,random_keys=False):
        self.NCM = NeteaseCloudMusic(random_keys)
        self.DL = Downloader(session=session,pool_size=pool_size,buffer_size=buffer_size)
        # Initalization of other classes
        self.temp,self.output,self.merge_only = temp,output,merge_only
        self.pool_size = pool_size
    
    def ShowDownloadStatus(self):
        '''
            Shows downloader info
        '''
        content = self.DL.report('''\nDownloading....{1} in queue,{2} not finished\n{0}''')
        logger.info(content + Cursor.UP(content.count('\n') + 1))
        time.sleep(1)

    def GenerateDownloadPath(self,id='', filename='', folder=''):
        '''
            Generates output path with its leaf folders and such.Similar to mktree

            Specify folder to change the root folder somewhere else
        '''
        def normalize(s):
            mapping = {
                '\\':' ',
                '/' :'',
                ':' :'：',
                '*' :'·',
                '?' :'？',
                '"' :'”',
                '<' :'《',
                '>' :'》',
                '|' :'、'
            }
            for k,v in mapping.items():
                s = s.replace(k,v)
            return s
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
        logger.debug('Queued download ...%s -> ...%s' % (url[-16:],path[-16:]))

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
        return info

    def QueueDownloadAllSongsInAlbum(self,id, quality='lossless', folder=''):
        '''
            This will get every song's ID inside the album resovled

            Note that extra info will be stored inside the JSON that the api sent
        '''
        info = self.NCM.GetAlbumInfo(id)
        try:
            name, creator = info['title'], info['author']
        except Exception as e:
            logger.error('Failed to fetch Album info:%s' % e)
            return
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
        return info

    def QueueDownloadAllSongsInPlaylist(self,id, quality='lossless', folder=''):
        '''
            This will try and get all songs' ID and such in the playlist,then try to download them.

            The strcuture is very similar to the album one,but with some minor twists
        '''
        info = self.NCM.GetPlaylistInfo(id)
        try:
            name, creator = info['playlist']['name'], info['playlist']['creator']['nickname']
        except Exception as e:
            logger.error('Failed to fetch Playlist info:%s' % e)
            return
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
        return info

    def DownloadSongLyrics(self,id, folder=''):
        '''
            This will only write the song's lyrics into JSON (named lyrics.json) to a certain directory.
        '''
        lyrics = self.NCM.GetSongLyrics(id)
        target = self.GenerateDownloadPath(filename='lyrics.json', folder=folder)
        open(target, mode='w', encoding='utf-8').write(json.dumps(lyrics))
        # Writes lyrics to JSON file
        return lyrics

    def LoadLyrics(self,folder):
        '''
            Converts the lyrics JSON format into a dictionary
        '''
        lyrics = self.GenerateDownloadPath(filename='lyrics.json', folder=folder)
        # Locate lyric file
        if not os.path.exists(lyrics):
            logger.error('Missing lyrics.json,LRC will not be parsed')
            return {}
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
            logger.warn('Missing meta.json,will skip meta info parsing')
            meta = {
                'title':'undefined',
                'album':'undefined',
                'author':'undefined'
            }
        else:
            meta = json.loads(open(meta, encoding='utf-8').read())
        # Load JSON for future purposes
        lrc = f"""[ti:{meta['title']}]\n[al:{meta['album']}]\n[au:{meta['author']}]\n[re:PyNCM]\n"""

        for timestamp in lyrics.keys():
            newline = '[%s]' % timestamp
            newline += '\t'.join(lyrics[timestamp])
            lrc += '\n' + newline
        path = self.GenerateDownloadPath(
            filename='{1} - {0}.{2}'.format(meta['title'], meta['author'], 'lrc'), folder=export)
        open(path, mode='w', encoding='utf-8').write(lrc)
        logger.debug('Downloaded lyrics ...%s' % path[-16:])
        return lrc

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
            logger.error('audio.m4a / audio.mp3 / audio.flac is missing,Cannot continue formatting!')
            return

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
            logger.debug('Exported audio to path %s' % path[-16:])
        except Exception as e:
            logger.error('While copying audio file:%s' % e)
        return path

    def DownloadSongAudio(self,id, quality='lossless', folder=''):
        '''
            Download Audio,and wait for it to finish
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        self.QueueDownloadSongAudio(id, quality, folder)
        self.DL.wait(func=self.ShowDownloadStatus)
        logger.debug('Downloaded audio file for id %s' % id)
        return True

    def DownloadSongInfo(self,id, folder=''):
        '''
            Download info,and wait for it to finish
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        self.QueueDownloadSongInfo(id, folder)
        self.DL.wait(func=self.ShowDownloadStatus)
        logger.debug('Downloaded audio meta for id %s' % id)
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

    def DownloadAll(self,id, quality='lossless', folder=''):
        '''
            Download everything we need,then wait for download to finish.
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        # Download meta and cover.Note that cover is downloaded asynchronously
        self.QueueDownloadSongInfo(id, folder)
        # Download lyrics
        self.DownloadAndFormatLyrics(id)
        # Download song.Not that audio file is downloaded asynchronously
        self.QueueDownloadSongAudio(id, quality, folder)
        self.DL.wait(func=self.ShowDownloadStatus)
        logger.debug('Downloaded everything for id %s' % id)
        return True

    def DownloadAllAndMerge(self,id, quality='lossless', folder=''):
        '''
            This will merge the infomation once download is finished
        '''
        if not folder:
            folder = self.GenerateDownloadPath(id=id, folder=folder)
        self.DownloadAll(id, quality, folder)
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
            if not self.merge_only:
                logger.info('Queuing download for specified resources...')
                queue_func(id, quality, folder)
                self.DL.wait(func=self.ShowDownloadStatus)
                # Queue then wait
            processed = 0
            def tag(subfolder):
                self.FormatLyrics(subfolder)
                self.FormatSong(subfolder)
            # Start merging every subfolder via threadpool,where it's a mutation of the Downloader
            pool = Downloader(worker=PoolWorker,pool_size=8)
            for sub in os.listdir(folder):
                pool.append(tag, os.path.join(folder,sub))
            print('\n' * 15)
            def wait():
                logger.info(f'Tagging... {len(os.listdir(folder)) - pool.task_queue.unfinished_tasks} / {len(os.listdir(folder))}{Cursor.UP(1)}')
                time.sleep(1)
            print()
            pool.wait(func=wait)
        return wrapper

    def DownloadAllSongsInPlaylistAndMerge(self,id, quality='lossless', folder=None,merge_only=False):
        '''
            Downloads all songs in a playlist into selected folder

                id          :       Song ID
                quality     :       Song Quality
                folder      :       Output folder
                merge_only  :       Merge by id from 'folder',Only use this if you 
                                    Have finished downloading first
        '''
        return self.MutilWrapper(self.QueueDownloadAllSongsInPlaylist)(id, quality, folder,merge_only)

    def DownloadAllSongsInAlbumAndMerge(self,id, quality='lossless', folder=None,merge_only=False):
        '''
            Downloads all albums in a playlist into selected folder

                id          :       Song ID
                quality     :       Song Quality
                folder      :       Output folder
                merge_only  :       Merge by id from 'folder',Only use this if you 
                                    Have finished downloading first
        '''
        return self.MutilWrapper(self.QueueDownloadAllSongsInAlbum)(id, quality, folder,merge_only)
