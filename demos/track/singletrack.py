import pyncm,getpass,hashlib,os,logging
from pyncm import GetCurrentSession,LoadSessionFromString
SESSION_FILE = 'session.ncm'
def login(session_file):
    def save():
        with open(session_file,'w+') as f:
            f.write(pyncm.DumpSessionAsString(GetCurrentSession()))
        return True
    def load():
        if not os.path.isfile(session_file):return False
        with open(session_file) as f:
            pyncm.SetCurrentSession(LoadSessionFromString(f.read()))
        return pyncm.GetCurrentSession().login_info['success']    
    if load():
        return print('[-] Recovered session data of [ %s ]' % pyncm.GetCurrentSession().login_info['content']['profile']['nickname']) or True
    phone = input('Phone >>>')
    passw = getpass.getpass('Password >')
    pyncm.login.LoginViaCellphone(phone,passw)
    print('[+]',pyncm.GetCurrentSession().login_info['content']['profile']['nickname'],'has logged in')
    return save()
login(SESSION_FILE)
# 登录有关，大可不看
print(pyncm.track.GetTrackAudio(30987348,bitrate=3200 * 1000)) # 注意是 3200 k
'''一般地 320k即以上即 flac, 320k及以下即 mp3,96k及以下即 m4a
取决于歌曲；若 bitrate 值非常大，则回传最佳音质歌曲（如本例）
'''