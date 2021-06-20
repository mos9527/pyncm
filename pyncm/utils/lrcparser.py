'''Another lrc file parser'''
import re
from collections import defaultdict

def LrcProperty(tagname):    
    def wrapper(func):
        @property
        def _wrapper(self):
            if not hasattr(self,tagname):return Exception(tagname)
            try:
                return getattr(self,tagname)
            except:
                # So this is how we enmurate all the attributes on startup
                # As no values are assigned (not inintalized),they will surely cause errors
                # Making it fallback to another value.Here,we fallback to its raw tagname
                return Exception(tagname)
        @_wrapper.setter
        def _wrapper(self,v):
            setattr(self,tagname,v)
        return _wrapper  
    return wrapper

class LrcRegexes:
    LIDTag_= re.compile(r'(?<=\[)[^\[\]]*(?=\])')
    LIDTag_Type = re.compile(r'[a-z]{2,}(?=:)')
    LIDTag_Content = re.compile(r'(?<=[a-z]{2}:).*')
    LLyrics_ = re.compile(r'[^\[\]]*$')
    LBrackets = re.compile(r'(?<=\[).*(?=\])')
    LTimestamp = re.compile(r'\d*[\.,:]\d*[\.,:]\d*')
# region Static methods
# Timestamp parsers
def stamp2tag(timestamp):
    mm = int(timestamp / 60)
    ss = int((timestamp - mm * 60))
    xx = int((timestamp - mm * 60 - ss) * 100) # We'd use standard 100th of a second here
    mm,ss,xx = str(mm).rjust(2,'0'),str(ss).rjust(2,'0'),str(xx).rjust(2,'0')
    return f'{mm}:{ss}.{xx}'                    
    
def tag2stamp(IDTag):
    IDTag = ''.join(LrcRegexes.LTimestamp.findall(IDTag))
    if not IDTag:return None
    div = IDTag.split(':') 
    if (len(div)==2):
        mm,ss = div
        ss,xx = ss.split('.') # xx is hunderth of a second,but NE didn't think so
    else:
        mm,ss,xx = div
    timestamp = int(mm) * 60 + int(ss) + int(xx) * (0.1 ** len(xx)) # <- workaround
    return timestamp
# endregion

class LrcParser:
    '''Parses lrc into mutable dict-like objects'''
    # region Properties from Wikipedia [https://en.wikipedia.org/wiki/LRC_(file_format)]
    @LrcProperty('ar')
    def Artist(self):pass
    @LrcProperty('al')
    def Album(self):pass
    @LrcProperty('ti')
    def Title(self):pass
    @LrcProperty('au')
    def Author(self):pass
    @LrcProperty('length')
    def Length(self):pass
    @LrcProperty('by')
    def LRCAuthor(self):pass
    @LrcProperty('offset')
    def Offset(self):pass
    @LrcProperty('re')
    def Program(self):pass
    @LrcProperty('ve')
    def ProgramVersion(self):pass
    # endregion
    
    def __init__(self,lrc=''):
        '''Takes lyrics in `LRC` format,then provides lyrics based on timestamps'''
        # Parsing lrc,line by line
        def EnmurateAttributes():
            for m in dir(self):
                if any(f in m for f in ['__','Add','Load','Clear','Find','Update','Dump','lyrics']):continue
                yield (m,str(getattr(self,m)))        
        self.lrcAttributes = list(EnmurateAttributes())
        # This function will only work when no attributes are defined
        self.lyrics = defaultdict(list)
        if not lrc:
            # empty input,we are creating lyrics then
            return
        else:self.LoadLrc(lrc)

    @property
    def lyrics_sorted(self):
        '''Returns sorted version of the lyrics'''
        return defaultdict(list,sorted(self.lyrics.items()))        

    def LoadLrc(self,lrc):
        '''Loads a LRC formmated lryics file'''
        for line in lrc.split('\n'):
            IDTag           =         LrcRegexes.LIDTag_       .findall(line)
            IDTagType       = ''.join(LrcRegexes.LIDTag_Type   .findall(''.join(IDTag)))
            IDTagContent    = ''.join(LrcRegexes.LIDTag_Content.findall(''.join(IDTag)))
            Lyrics          = ''.join(LrcRegexes.LLyrics_      .findall(line))
            if IDTagType:
                # Tag's type is set,write as class attribute
                setattr(self,IDTagType,IDTagContent)
            elif IDTag:
                # Tag's type is not set but we got the values,treat as lyrics
                # We'll use the timestamp (into seconds) as lyrics' keys,as hashtables can handle that            
                try:
                    for _IDTag in IDTag:
                        # Some LRC lyrics would pile a bunch of timestamps in on line,like 
                        #   [00:01.12][00:08.12]Yeah                        
                        timestamp = tag2stamp(_IDTag)
                        if timestamp is not None and timestamp >= 0:
                            if not isinstance(self.Offset,Exception):timestamp += float(self.Offset)
                            if Lyrics:self.lyrics[timestamp].append((_IDTag,Lyrics)) # Ignore empty lines
                except:
                    pass
        self.lyrics = self.lyrics_sorted # sort stuff once loaded

    def AddLyrics(self,timestamp,value):
        # Add 1 or multiple line(s) of lyrics with the same timestamp in seconds 
        if not isinstance(value,list):value = [value]
        for v in value:self.lyrics[timestamp].append((stamp2tag(timestamp),v))
        self.lyrics = self.lyrics_sorted # this isn't too much for previously sorted items though
    
    def ClearLyrics(self):
        # Clears the lyrics buffer
        self.lyrics.clear()

    def UpdateLyrics(self,iterable,timestamp_function,lyrics_function):
        '''This function takes an iterable,a timestamp function,and a lyrics function
        
        And for every item in the iterable,timestamp and lyrics will be fetch via the said functions,then get added to our buffer
        '''
        for line in iterable:
            timestamp = timestamp_function(line)
            lyrics    = lyrics_function(line)
            self.AddLyrics(timestamp,lyrics)

    def DumpLyrics(self,delimiter='\t'):
        '''Format current lyrics buffer then spits out a LRC formatted string'''
        lrc = ''
        # Adding tags
        for prop,attr in self.lrcAttributes:
            value = getattr(self,prop)
            if not isinstance(value,Exception): # If such value do exist
                lrc += f'[{attr}:{value}]' + '\n'        
        # Adding lyrics
        for timestamp,lyrics in self.lyrics.items(): # write the sorted one
            Lyrics = []
            for tag,_lyric in lyrics:
                Lyrics.append(_lyric)
            lrc += '\n' + f'[{stamp2tag(timestamp)}]{delimiter.join(Lyrics)}' 
        return lrc # Done
    
    @staticmethod
    def Find(lyrics,timestamp):
        '''Finds closest match in our hashable
            
            lyrics  :   From `lrcparser.lyrics_sorted`

            Returns `(timestamp_seconds,lyrics,indexof)`

            Returns None if the match isn't inside the window
        '''
        def search(val,src:list,l,r):    
            '''Binary serach'''            
            pivot = (l+r)>>1
            if (l >= r or pivot == l or pivot == r):return pivot            
            in_between = (pivot<=0 or (src[pivot-1] <= val)) and val <= src[pivot]            
            if in_between:            
                if src[pivot] == val:
                    return pivot
                elif src[pivot - 1] == val:
                    return pivot - 1
                else:
                    return pivot
            return search(val,src,pivot,r) if src[pivot] < val else search(val,src,l,pivot)        
        timestamps = list(lyrics.keys())
        index      = search(timestamp,timestamps,0,len(lyrics))        
        return (timestamps[index],lyrics[timestamps[index]],index)