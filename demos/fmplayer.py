'''古典FM 、 DIFM 播放

- 需要安装 ffplay；或可根据其它播放器修改 `executable` 变量 
 - e.g. play --title "%(title)s" -i "%(url)s"
'''
executable = 'ffplay   -noborder -v quiet -x 1920 -y 200 -hide_banner -loglevel info -autoexit -showmode 2 -window_title "%(title)s" -i "%(url)s"'

from pyncm.utils.helper import TrackHelper
import pyncm,os,sys,random,logging,colorama
colorama.init()
logging.disable(logging.ERROR)
stdout_write = sys.stdout.write

def alt_write(s):
    stdout_write(s)
    open(__file__.replace('.py','.log'),encoding='utf-8',mode='a').write(s) # we would save our playlist though
sys.stdout.write = alt_write
def myfm():
    if not pyncm.GetCurrentSession().login_info['success']:
        print('🔑 需要登陆')
        phone = input('手机号：')
        passw = input('  密码：')
        pyncm.login.LoginViaCellphone(phone,passw)
    return pyncm.miniprograms.radio.GetMoreRaidoContent()
bpm=10
def sportsfm():
    global bpm
    bpm += random.randrange(20,50)
    bpm = bpm % 200
    print('🏃‍ 每分钟步数:',bpm)
    return pyncm.miniprograms.sportsfm.GetSportsFMRecommendations(limit=1,bpm=bpm)
sem = {
    'di':(pyncm.miniprograms.difm.GetCurrentPlayingTrackList,'Di.FM'),
    'cl':(pyncm.miniprograms.zonefm.GetFmZoneInfo,'古典 FM'),
    'sports':(sportsfm,'跑步 FM'),
    'my':(myfm,'私人 FM')}
sel = input('🌏 选择音源 %s:' % '    '.join([ k + ':' + v[1] for k,v in sem.items() ]) )

if not sel in sem.keys():
    new_sel = list(sem.keys())[random.randrange(0,len(sem))]
    print('❎ 音源 %s 无效 - 选择音源 %s' % (sel,new_sel))
    sel = new_sel

while True:
    tracks = sem[sel.lower()][0]()
    for track in tracks['data'] if isinstance(tracks['data'],list) else tracks['data']['list']:
        tr = TrackHelper(track)
        print(f'''🎵 正在播放 [https://music.163.com/#/song?id={track['id']}]''')
        print(f" {tr.TrackName} - {' / '.join(tr.Artists)}")        
        audio = pyncm.apis.track.GetTrackAudio(track['id'])['data'][0]['url'] if not 'audio' in track.keys() else track['audio']
        try:
            print('\33]0;%s\a' % tr.TrackName)
            os.system(executable % {'title':track['name'],'url':audio})
        except KeyboardInterrupt:
            print('⏩ 下一首')
    print('🌏 刷新音源...')