'''古典FM 、 DIFM 播放

- 需要安装 ffplay；或可根据其它播放器修改 `executable` 变量 
 - e.g. play --title "%(title)s" -i "%(url)s"
'''
executable = 'ffplay -alwaysontop -v quiet -x 400 -y 200 -hide_banner -loglevel info -autoexit -showmode 2 -window_title "%(title)s" -i "%(url)s"'

import pyncm,os,sys
stdout_write = sys.stdout.write

def alt_write(s):
    stdout_write(s)
    open(__file__.replace('.py','.log'),encoding='utf-8',mode='a').write(s) # we would save our playlist though
sys.stdout.write = alt_write

sel = input('🌏 选择音源 [ di:Di.FM ; cl:CLASSICAL ]:')
sem = {'di':pyncm.miniprograms.difm.GetCurrentPlayingTrackList,'cl':pyncm.miniprograms.zone.GetFmZoneInfo}
if not sel in sem.keys():
    print('⚠ 音源 %s 无效 - 选择音源 %s' % (sel,list(sem.keys())[0]))
    sel = list(sem.keys())[0]
while True:
    tracks = sem[sel.lower()]()
    for track in tracks['data'] if isinstance(tracks['data'],list) else tracks['data']['list']:
        print(f'''🎵 正在播放 [https://music.163.com/#/song?id={track['id']}]''')
        print(f"    {track['name']} - {track['album']['name'] if 'album' in track.keys() else track['artist']}")
        audio = pyncm.apis.track.GetTrackAudio(track['id'])['data'][0]['url'] if not 'audio' in track.keys() else track['audio']
        try:
            os.system(executable % {'title':track['name'],'url':audio})
        except KeyboardInterrupt:
            print('⏩ 下一首')