from logging import log
from os import stat
import pyncm,getpass
from pyncm import GetCurrentSession,LoadSessionFromString
from os.path import isfile
status = {'succeeded':[],'failed':[]}
def Testpoint(func):
    def wrapper():
        global status
        result = func()
        if (not result) or (isinstance(result,dict) and (not 'code' in result or result['code'] != 200)):
            status['failed'].append((func,result))
        else:
            status['succeeded'].append((func,result))
        return result
    return wrapper
def Results():
    print('Diagnose Results ================')
    print('  - SUCCEEDED')
    for func,result in status['succeeded']: 
        print(f'    [-] {func.__name__} {result}')
    if not status['succeeded']:print('     None')
    print('  - FAILED')
    for func,result in status['failed']:
        print(f'    [!] {func.__name__} {result}')        
    if not status['failed']:print('     None')
    print('END OF DIAGNOSE  ================')
'''Login'''
SESSION_DUMP_FILENAME = 'session.ncm'
@Testpoint
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
            pyncm.GetCurrentSession().login_info['content']['profile']['nickname']) or True
        except KeyboardInterrupt:
            pass
    phone = input('手机号 >>>')
    passw = getpass.getpass('密码 >')
    pyncm.login.LoginViaCellphone(phone,passw)
    print(pyncm.GetCurrentSession().login_info['content']['profile']['nickname'],'登陆成功')
    return save()
'''checkToken required APIs'''
@Testpoint
def test_create_playlist():
    return pyncm.apis.playlist.SetCreatePlaylist('PyNCM')
login()
r1 = test_create_playlist()
@Testpoint
def test_delete_playlist():
    if r1['code'] != 200:return False    
    return pyncm.apis.playlist.SetRemovePlaylist(r1['id'])
r2 = test_delete_playlist()
@Testpoint
def test_fetch_fav_artists():
    return pyncm.apis.user.GetUserArtistSubs()    
r3 = test_fetch_fav_artists()
@Testpoint
def test_fetch_track_lyrics_with_romaji():
    return pyncm.apis.track.GetTrackLyrics('31140606')
r4 = test_fetch_track_lyrics_with_romaji()
Results()