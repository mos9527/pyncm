import logging,time
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
    def ID(self):
        '''Track ID'''
        return self.track['id']

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
        '''The cover URL of the track's album'''
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
        return f'{self.TrackName} - {",".join(self.Artists)}'
    _illegal_chars = set('\x00\\/:*?"<>|')
    @TrackHelperProperty()
    def SanitizedTitle(self):
        '''Sanitized title for FS compatibility; Limits max length to 200 chars,and substitutes illegal chars with their full-width counterparts'''
        def _T(s,l=100):
            return ''.join([c if not c in self._illegal_chars else chr(ord(c)+0xFEE0) for c in s])[:l]
        return f'{_T(self.TrackName,100)} - {_T(",".join(self.Artists),100)}'