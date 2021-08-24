import pyncm,getpass,os
import os,sys
from phone import login
sys.path.extend(['demos/cloudupload','demos/login'])
assert login(),"登陆失败"
print(pyncm.track.GetTrackAudio(input('歌曲 ID:'),bitrate=3200 * 1000))
'''一般地 320k即以上即 flac, 320k及以下即 mp3,96k及以下即 m4a
取决于歌曲；若 bitrate 值非常大，则回传最佳音质歌曲（如本例）
'''