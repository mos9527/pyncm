'''
以下 .pyncm 即为你保存的登陆凭据
---
使用例 : 同步个人创建的歌单到`NetEase/[专辑名]`
    python .\demos\歌单同步.py --load .pyncm --quality hires --output NetEase/{album}
使用例 : 同步个人创建+收藏的歌单到`NetEase/[专辑名]`,并保存 M3U 播放列表
    python .\demos\歌单同步.py --load .pyncm --quality hires --output NetEase/{album} --user-bookmarks --save-m3u NetEase/PLAYLIST.m3u
使用例 : 同步某一歌单到`NetEase/[专辑名]`
    python .\demos\歌单同步.py --load .pyncm --quality hires --output NetEase/{album} https://music.163.com/playlist?id=988690134
'''
from sys import argv
from os import walk,path,remove
from pyncm.__main__ import parse_args ,PLACEHOLDER_URL,__main__
from pyncm import GetCurrentSession,SetCurrentSession,LoadSessionFromString
from pyncm.utils.helper import UserHelper
# 指定 quit_on_empty_args=False 便于传入空 ID
args, _ = parse_args(quit_on_empty_args=False)
print("[-] 读取登录信息 : %s" % args.load)
SetCurrentSession(LoadSessionFromString(open(args.load).read()))
print("[*] 用户 : %s" % UserHelper(GetCurrentSession().uid).UserName)
try:
    # 使用未模板化的最高级目录做输出目录起点
    output = args.output[:args.output.index('{')]
except IndexError:
    output = args.output
print("[*] 输出文件夹起点 : %s" % output)
def normalize(path):
    return path.replace('\\','/') # 统一 Windows/Unix 路径格式
# 平面化目录结构，准备后期比对
file_tree = [normalize(path.join(root,file)) for root, dirs, files in walk(output,topdown=False) for file in files]
# 调用 pyncm 下载
if args.url == PLACEHOLDER_URL:
    # 未填入 ID 则使用用户本人歌单
    argv.append('https://music.163.com/#/user/home?id=%s' % GetCurrentSession().uid)
argv.append("--no-overwrite")
# 不覆写已存在歌曲
# argv 传参，调用 __main__ 即可
queuedTasks, failed_ids = __main__(return_tasks=True)
# 无视拓展名的文件白名单
file_tree_whitelist = [normalize(task.save_as) for task in queuedTasks]
# 只删除这些拓展名的文件
extension_blacklist = {'m4a','mp3','flac','ogg','lrc','ass'}
for file in file_tree:
    delete_flag = True
    for file_whitelist in file_tree_whitelist:
        if file.startswith(file_whitelist):
            delete_flag = False
            break
    if delete_flag:
        ext = file.split('.')[-1].lower()
        if ext in extension_blacklist:            
            try:
                print('[!] 删除 %s' % file)
                remove(file)
            except Exception as e:
                print('[!!] 删除 %s 失败: %s' % (file,e))