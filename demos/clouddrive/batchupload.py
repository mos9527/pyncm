import os,sys
sys.path.extend(['demos/cloudupload','demos/login'])
from cloudupload import upload_one
from phone import login
from time import sleep


if __name__ == '__main__':    
    assert login(),"登陆失败"
    tracks = input('[-] Path to folder:')
    for path in os.listdir(tracks):
        full_path = os.path.join(tracks,path)
        print('[-] Uploading %s' % path)
        while True:
            try:
                upload_one(full_path)
                break
            except Exception as e:
                print('[!] %s - retrying...' % e)
                sleep(5)
    print('[-] All done.')


