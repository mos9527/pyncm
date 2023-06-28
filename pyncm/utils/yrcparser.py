import re
from typing import List
from json import loads
from .lrcparser import LrcRegexes,stamp2tag

CurlyBracketRegex = re.compile(r'^{.*}$')
Timestamp2Regex = re.compile(r'^\[(?P<t_begin>\d*),(?P<t_duration>\d*)\]')
YrcBlock46Regex = re.compile(r'(\((?P<t_begin>\d*),(?P<t_duration>\d*),(?P<t_unk>\d*)\)(?P<text>[^\(]*))')

class TimestampedObject:
    # In milliseconds
    _t_begin : float = -1
    _t_duration : float = -1
    _t_end : float = -1

    @property
    def is_complete(self):
        return self._t_begin > 0 and self._t_duration > 0 and self._t_end > 0
    @property
    def t_begin(self):
        return self._t_begin
    @t_begin.setter
    def t_begin(self,value):
        self._t_begin = int(value)
    @property
    def t_duration(self):
        return self._t_duration
    @t_duration.setter
    def t_duration(self,value):
        self._t_duration = int(value)
        self._t_end = self._t_begin + self._t_duration
    @property
    def t_end(self):
        return self._t_end
    @t_end.setter
    def t_end(self,value):
        self._t_end = int(value)
        self._t_duration = self._t_end - self.t_begin
    
class YrcBlock(TimestampedObject):
    text : str = None
    meta : dict = None
    def __repr__(self) -> str:
        if self.meta:
            return '<meta=%s>' % self.meta
        return self.text

class YrcLine(TimestampedObject,list):
    def new_block(self):
        block = YrcBlock()
        self.append(block)
        return block 
    
    def __repr__(self) -> str:
        return 'start=%d duration=%d %s' % (self.t_begin,self.t_duration,''.join([str(b) for b in self]))

class YrcParser(list):
    @staticmethod
    def extract_meta(meta):
        tgt = meta.get('c',meta)
        assert type(tgt) == list
        return ''.join([i.get('tx','') for i in tgt])

    def __init__(self, version : int,yrc : str):
        self.yrc = yrc
        self.parser = YrcParser46 # TODO: Clarify version differences        
        
    def parse(self):
        self.parser = self.parser(
            -1, # Dummy number to prevent subclassing
            self.yrc
        ).parse()        
        self.parser.fixup()
        return self.parser

    def fixup(self):
        for i,line in enumerate(self):
            line : YrcLine
            if i > 0 and not self[i - 1].is_complete:
                self[i - 1].t_end = line.t_begin
                              
class YrcParser46(YrcParser):
    def parse(self):    
        for line in self.yrc.split('\n'):
            if not line:
                continue
            new_line = YrcLine()
            BracketTag = LrcRegexes.LIDTag.findall(line)
            if not BracketTag:                
                JsonTag = CurlyBracketRegex.findall(line)                
                if JsonTag:
                    # Only one per line
                    meta = loads(line)
                    new_line.t_begin = meta['t']
                    block = new_line.new_block()       
                    block.t_begin = new_line.t_begin
                    block.meta = meta                    
            else:
                TimestampTag = next(Timestamp2Regex.finditer(line)).groupdict()                
                new_line.t_begin = TimestampTag.get('t_begin')
                new_line.t_duration = TimestampTag.get('t_duration') # milliseconds
                for YrcBlockRaw in YrcBlock46Regex.finditer(line):
                    new_block_raw = YrcBlockRaw.groupdict()
                    new_block = new_line.new_block()
                    new_block.t_begin = new_block_raw.get('t_begin')
                    new_block.t_duration = new_block_raw.get('t_duration') # centiseconds
                    new_block.t_duration *= 10 # to milliseconds
                    new_block.text = new_block_raw.get('text')                    
            self.append(new_line)        
        return self
    
class ASSWriter():
    def __init__(self) -> None:
        self.content = '''[Script Info]
[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''

    def begin_line(self,start_millis,end_millis):
        self.content += '''Dialogue: 0,0:%s,0:%s,,,0,0,0,,''' % (stamp2tag(start_millis / 1000),stamp2tag(end_millis / 1000))

    def add_meta(self,text):
        self.content += text

    def add_syllable(self,duration,text):
        # From https://aegi.vmoe.info/docs/3.1/ASS_Tags/
        # The duration is given in centiseconds, ie. a duration of 100 is equivalent to 1 second
        self.content += r'''{\K%d}%s''' % (duration / 100,text)

    def end_line(self):
        self.content += '\n'