from __init__ import login
from pyncm.apis.track import GetTrackAudio

assert login(), "登录失败"
print(GetTrackAudio(input("歌曲 ID:"), bitrate=3200 * 1000))
"""一般地 320k即以上即 flac, 320k及以下即 mp3,96k及以下即 m4a
取决于歌曲；若 bitrate 值非常大，则回传最佳音质歌曲（如本例）
"""
