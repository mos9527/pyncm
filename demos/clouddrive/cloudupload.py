import pyncm,hashlib,os,sys
sys.path.insert(0,'demos/login')
from phone import login

def md5sum(file):
    md5sum = hashlib.md5()
    with open(file,'rb') as f:
        while chunk:=f.read():
            md5sum.update(chunk)
    return md5sum

def upload_one(path):
    fname = os.path.basename(path)
    fext = path.split('.')[-1]
    '''Parsing file names'''
    fsize = os.stat(path).st_size
    md5 = md5sum(path).hexdigest()
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
            open(path,'rb'),
            md5,fsize,token['objectKey'],token['token']
        )
        print('[-] Response:\n  ',upload_result)    
    print(f'''[!] Assuming upload has finished,preparing to submit    
    ID  :   {songId}
    MD5 :   {md5}
    NAME:   {fname}''')
    submit_result = pyncm.cloud.SetUploadCloudInfo(token['resourceId'],songId,md5,fname,fname,pyncm.GetCurrentSession().login_info['content']['profile']['nickname'],bitrate=1000)    
    '''3. 提交资源'''
    print('[-] Response:\n  ',submit_result)
    '''4. 发布资源'''
    publish_result = pyncm.cloud.SetPublishCloudResource(submit_result['songId'])
    print('[-] Response:\n  ',publish_result)

if __name__ == "__main__":
    login()
    # login via phone,may change as you like
    upload_one(input('[-] Path to file:'))
    