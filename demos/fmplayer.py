'''古典FM 、 DIFM 播放

- 需要安装 ffplay；或可根据其它播放器修改 `executable` 变量 
 - e.g. play --title "%(title)s" -i "%(url)s"
'''
executable = 'ffplay -autoexit -left 0 -top 0 -x 1280 -v quiet -hide_banner -loglevel info -window_title "%(title)s" -i "%(url)s"'

from os import times
from os.path import isfile
from pyncm.apis.track import GetTrackDetail
from pyncm import GetCurrentSession, LoadSessionFromString
from pyncm.utils.helper import TrackHelper
from pyncm.utils.lrcparser import LrcParser
import pyncm,sys,random,logging,colorama,getpass,time,subprocess

PIPE_POLL_INTERVAL = 1/60
LYRICS_WINDOW = 1
SESSION_DUMP_FILENAME = 'fmplayer.ncm'

colorama.init()
logging.disable(logging.ERROR)
stdout_write = sys.stdout.write
lyrics=LrcParser()

def alt_write(s):
    stdout_write(s)
    open(__file__.replace('.py','.log'),encoding='utf-8',mode='a').write(s) # we would save our playlist though
sys.stdout.write = alt_write

def login():
    def save():
        with open(SESSION_DUMP_FILENAME,'w+') as f:
            f.write(pyncm.DumpSessionAsString(GetCurrentSession()))
        return True
    def load():
        if not isfile(SESSION_DUMP_FILENAME):return False
        with open(SESSION_DUMP_FILENAME) as f:
            pyncm.SetCurrentSession(LoadSessionFromString(f.read()))
        return pyncm.GetCurrentSession().login_info['success']    
    print('需要登陆')  
    if load():
        try:
            return input('按回车使用保存的账户 %s ,或 Ctrl + C 输入新令牌>>>' %
            pyncm.GetCurrentSession().login_info['content']['profile']['nickname'])
        except KeyboardInterrupt:
            pass
    phone = input('手机号 >>>')
    passw = getpass.getpass('密码 >')
    pyncm.login.LoginViaCellphone(phone,passw)
    print(pyncm.GetCurrentSession().login_info['content']['profile']['nickname'],'登陆成功')
    save()
def myfm():
    not pyncm.GetCurrentSession().login_info['success'] and login()
    return pyncm.miniprograms.radio.GetMoreRaidoContent()
bpm=10
def sportsfm():
    global bpm
    bpm += random.randrange(20,50)
    bpm = bpm % 200
    print('每分钟步数:',bpm)
    return pyncm.miniprograms.sportsfm.GetSportsFMRecommendations(limit=1,bpm=bpm)
last=0    
def execute(command):
    def getTimestamp(line):
        if line and 'M-A' in line:
            return float(line.split(' ')[0])        
        return -1
    global last
    process = subprocess.Popen(command,stderr=subprocess.PIPE)
    returncode = None
    while returncode == None:
        returncode = process.poll()
        # Break the loop once process is killed       
        time.sleep(PIPE_POLL_INTERVAL) 
        newline = bytearray()
        while (process.poll() == None):
            c=process.stderr.read(1)
            if (c==b'\r' or c==b'\n' or c == b'\x13'):break
            newline.extend(c)
        newline = newline.decode().strip()    
        timestamp = getTimestamp(newline)
        if timestamp >=0:
            if lyrics.lyrics:
                ts,lrc,index = LrcParser.Find(lyrics.lyrics,timestamp)
                if ts-timestamp<=LYRICS_WINDOW:
                    if (last != ts):
                        last = ts
                        print('\n\t'.join(l[1] for l in lrc))
def playlist():
    _id = input('输入歌单ID>>>')                    
    return pyncm.playlist.GetPlaylistInfo(_id)
def album():
    _id = input('输入专辑ID>>>')                    
    return {'data':pyncm.album.GetAlbumInfo(_id)['songs']}
sem = {
    'di':(pyncm.miniprograms.difm.GetCurrentPlayingTrackList,'Di.FM'),
    'cl':(pyncm.miniprograms.zonefm.GetFmZoneInfo,'古典 FM'),
    'sp':(sportsfm,'跑步 FM'),
    'al':(album,'专辑'),
    'pl':(playlist,'歌单™'),    
    'my':(myfm,'私人 FM')}
print(r''' _______  _________     _____   _____      __________.__                              
 \      \ \_   ___ \   /     \_/ ____\_____\______   \  | _____  ___.__. ___________  
 /   |   \/    \  \/  /  \ /  \   __\/     \|     ___/  | \__  \<   |  |/ __ \_  __ \ 
/    |    \     \____/    Y    \  | |  Y Y  \    |   |  |__/ __ \\___  \  ___/|  | \/ 
\____|__  /\______  /\____|__  /__| |__|_|  /____|   |____(____  / ____|\___  >__|    
        \/        \/         \/           \/                   \/\/         \/        
Version %s
''' % pyncm.__version__)
sel = input('选择音源\n%s\n>>>'%'\n'.join([ k.ljust(5) + ':   ' + v[1] for k,v in sem.items() ])).lower()[:2]
if not sel in sem.keys():
    new_sel = list(sem.keys())[-1]
    print('音源 %s 无效 - 选择音源 %s' % (sel,new_sel))
    sel = new_sel
while True:
    print('[',sem[sel.lower()][1],']')
    tracks = sem[sel.lower()][0]()    
    # getting tracks out from all sorts of dicts
    if 'data' in tracks:
        _tracks = tracks['data'] if isinstance(tracks['data'],list) else tracks['data']['list']
    elif 'playlist' in tracks:
        _tracks = GetTrackDetail([t['id'] for t in tracks['playlist']['trackIds']])['songs']
    else:
        _tracks = {}
    for track in _tracks:
        lyrics.ClearLyrics()
        last = 0
        tr = TrackHelper(track)
        audio = pyncm.apis.track.GetTrackAudio(track['id'])['data'][0]['url'] if not 'audio' in track.keys() else track['audio']
        lrc = pyncm.apis.track.GetTrackLyrics(track['id'])        
        print(f"{tr.TrackName} - {' / '.join(tr.Artists)} [https://music.163.com/#/song?id={track['id']}]")
        def preLrc():  
            if 'nolyric' in lrc:return lyrics.AddLyrics(1,' - 纯音乐，请欣赏 -')   
            if 'uncollected' in lrc:return lyrics.AddLyrics(1,' - 歌词未收集，请敬待曲库更新 -')                
            return lyrics.AddLyrics(1,' - 无歌词 -')
        rawlrcs= [lrc[k]['lyric'] for k in set(lrc.keys()).intersection({'lrc','tlyric','romalrc'}) if 'lyric' in lrc[k].keys()]                    
        for lrc_ in rawlrcs:lyrics.LoadLrc(lrc_)        
        try:
            print('\33]0;%s\a' % tr.TrackName,end='')
            execute(executable % {'title':track['name'],'url':audio})
        except KeyboardInterrupt:
            print('下一首')
    print('刷新音源...')