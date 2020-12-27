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
'''Login whatnot,try not to mind these'''
def md5sum(file):
    md5sum = hashlib.md5()
    with open(file,'rb') as f:
        while chunk:=f.read():
            md5sum.update(chunk)
    return md5sum

if __name__ == "__main__":
    login(SESSION_FILE)
    f = input('[-] Path to file:')
    fname = os.path.basename(f)
    fext = f.split('.')[-1]
    '''Parsing file names'''
    fsize = os.stat(f).st_size
    md5 = md5sum(f).hexdigest()
    print('[-] Checking file ( MD5:',md5,')')
    cresult = pyncm.cloud.GetCheckCloudUpload(md5)
    songId = cresult['songId']
    '''Before uploading,performing a sanity check is always a good idea'''
    if cresult['needUpload']:
        print('[+] %s needs to be uploaded ( %s B )' % (fname,fsize))
        '''There are couple procedures for uploading.Let's walk them through
        1. A Nos Token must be aquired for authentication'''
        token = pyncm.cloud.GetNosToken(fname,md5,fsize,fext)['result']
        '''2. The token is used to upload the object'''
        upload_result = pyncm.cloud.SetUploadObject(
            open(f,'rb'),
            md5,fsize,token['objectKey'],token['token']
        )
        print('[-] Response:\n  ',upload_result)    
    print(f'''[!] Assuming upload has finished,preparing to submit    
    ID  :   {songId}
    MD5 :   {md5}
    NAME:   {fname}''')
    submit_result = pyncm.cloud.SetUploadCloudInfo(songId,md5,fname,'testme','pyncm',bitrate=128)
    '''3. Lastly,we're submitting the resource'''
    print('[-] Response:\n  ',submit_result)
    