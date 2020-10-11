import qrlogin
print('Loaded module',qrlogin)
# Login with the qrcode gimmick we have here
import pyncm,random
# Testing track - `likes` a random track
r = pyncm.track.SetLikeTrack(random.randrange(10000,100000))
print(r)