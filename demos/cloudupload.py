from pyncm.utils.crypto import Crypto
import pyncm,getpass,hashlib,os,sys,urllib3
from pyncm import GetCurrentSession,LoadSessionFromString
SESSION_FILE = 'session.ncm'
urllib3.disable_warnings()
class upload_in_chunks(object):# sth from stackoverflow
    def __init__(self, filename, chunksize=1 << 13):
        self.filename = filename
        self.chunksize = chunksize
        self.totalsize = os.path.getsize(filename)
        self.readsofar = 0
    def __iter__(self):
        with open(self.filename, 'rb') as file:
            while True:
                data = file.read(self.chunksize)
                if not data:
                    sys.stderr.write("\n")
                    break
                self.readsofar += len(data)
                percent = self.readsofar * 1e2 / self.totalsize
                sys.stderr.write("Uploading...{percent:3.0f}%   \r".format(percent=percent))
                yield data
    def __len__(self):
        return self.totalsize
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
        return print('Recovered session data of [ %s ]' % pyncm.GetCurrentSession().login_info['content']['profile']['nickname']) or True
    phone = input('Phone >>>')
    passw = getpass.getpass('Password >')
    pyncm.login.LoginViaCellphone(phone,passw)
    print(pyncm.GetCurrentSession().login_info['content']['profile']['nickname'],'has logged in')
    return save()
login(SESSION_FILE)
GetCurrentSession().verify = False      
def md5sum(file):
    md5sum = hashlib.md5()
    with open(file,'rb') as f:
        while chunk:=f.read():
            md5sum.update(chunk)
    return md5sum

def upload(file):
    print('Calculating MD5 hash')
    md5 = md5sum(file).hexdigest()
    size=os.stat(file).st_size    
    token = pyncm.cloud.GetNosTokenAlloc(
        file,md5,size,file.split('.')[-1]
    )
    print('Tokenzied %s' % file,'  Hash %s' % md5,'  Size %s' % size,sep='\n')
    r = pyncm.cloud.UploadObject(
        upload_in_chunks(file),
        md5,
        size,
        token['result']['objectKey'],
        token['result']['token']
    )
    print(r)
    r1 = pyncm.cloud.UploadCloudInfoV2(
        token['result']['resourceId'],
        Crypto.RandomString(128,chars='0123456789ABCDEF'),
        'le radio.mp3',
        md5,
        file,
        128,
        'Download'
    )
    print(r1)
upload('notes/radio.mp3')