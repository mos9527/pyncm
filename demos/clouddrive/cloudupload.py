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
    '''网盘资源发布 4 步走：
    1.拿到上传令牌 - 需要文件名，MD5，文件大小'''
    token = pyncm.cloud.GetNosToken(fname,md5,fsize,fext)['result']    
    if cresult['needUpload']:
        print('[+] %s needs to be uploaded ( %s B )' % (fname,fsize))
        '''2. 若文件未曾上传完毕，则完成其上传'''
        upload_result = pyncm.cloud.SetUploadObject(
            open(f,'rb'),
            md5,fsize,token['objectKey'],token['token']
        )
        print('[-] Response:\n  ',upload_result)    
    print(f'''[!] Assuming upload has finished,preparing to submit    
    ID  :   {songId}
    MD5 :   {md5}
    NAME:   {fname}''')
    submit_result = pyncm.cloud.SetUploadCloudInfo(token['resourceId'],songId,md5,fname,'Le test','PyNCM',bitrate=1000)    
    '''3. 提交资源'''
    print('[-] Response:\n  ',submit_result)
    '''4. 发布资源'''
    publish_result = pyncm.cloud.SetPublishCloudResource(submit_result['songId'])
    print('[-] Response:\n  ',publish_result)
    