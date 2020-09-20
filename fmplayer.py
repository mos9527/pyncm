# For demoing miniprogram apis - requires FFPLAY to be installed
import pyncm,os,sys
stdout_write = sys.stdout.write
def alt_write(s):
    stdout_write(s)
    open(__file__.replace('.py','.log'),encoding='utf-8',mode='a').write(s) # we would save our playlist though
sys.stdout.write = alt_write

sel = input('🌏 Selecting soucre [di:Di.FM,cl:CLASSICAL]:')
sem = {'di':pyncm.miniprograms.difm.GetCurrentPlayingTrackList,'cl':pyncm.miniprograms.zone.GetFmZoneInfo}
if not sel in sem.keys():
    print('⚠ Key %s not supported,falling back to %s' % (sel,sem.keys()[0]))
    sel = sem.keys()[0]
while True:
    tracks = sem[sel.lower()]()
    for track in tracks['data'] if isinstance(tracks['data'],list) else tracks['data']['list']:
        print(f'''🎵 Playing [https://music.163.com/#/song?id={track['id']}]''')
        print(f"    {track['name']} - {track['album']['name'] if 'album' in track.keys() else track['artist']}")
        audio = pyncm.apis.track.GetTrackAudio(track['id'])['data'][0]['url'] if not 'audio' in track.keys() else track['audio']
        try:
            os.system(f"ffplay -hide_banner -loglevel info -autoexit -nodisp -i \"{audio}\"")
        except KeyboardInterrupt:
            print('⏩ Next track')