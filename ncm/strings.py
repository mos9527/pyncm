'''
@Author: greats3an
@Date: 2020-01-19 21:19:54
@LastEditors  : greats3an
@LastEditTime : 2020-02-11 20:05:56
@Site: mos9527.tooo.top
@Description: Logging system & multi-language support
'''
import time,locale
from colorama import init, Cursor, Fore;init()
# Basic multi language support
def LANG():
    '''Gets language settings,can be overridden
        0       :       ENGLISH
        1       :       SIMPILFILED CHINESE
    '''
    return 1 if 'zh' in str(locale.getdefaultlocale()[0]) else 0 

class strings():
    '''
        Log strings.Should be refered statictly (which means don't execute them) while used dymanicly
    '''
    def INIT(self): return 'PyNCM Bootstraped'
    def INIT_INIT(self): return """
\033[31m       
             p0000,      
       _p00 ]0#^~M!      
      p00M~  00          ______         _______ ______ _______  
     j0@^  pg0000g_     |   __ \___ ___|    |  |      |   |   |
    ]00   #00M0#M00g    |    __/|  |  ||       |   ----       |
    00'  j0F  00 ^Q0g   |___|   |___  ||__|____|______|__|_|__|
    00   00   #0f  00           |_____|                        
    00   #0&__#0f  #0c  ———————————————————————————————————————
    #0t   M0000F   00                 by greats3an @ mos9527.tooo.top 
     00,          j0#   SYANTAX HELP:
     ~00g        p00        --help,-h show manual
      `000pg,ppg00@         --help,-h 显示帮助文本
        ~M000000M^

    e.g. pyncm  --clear-temp song 1334780738                                              
\033[0m                      
    """
    # generated with http://patorjk.com/software/taag
    def INIT_INITALIZED_WITH_ARGS(self):return [
#id, operation, opt, password, username, clear_temp, merge_only, temp, output, pool_size,buffer_size
        """
Initalized with the following settings:
        ID                  :       {}
        Operation           :       {}
        Option              :       {}
        Password Hash       :       {}
        Phone               :       {}
        Do clear temp       :       {}
        Do merge only       :       {}
        Temporay folder     :       {}
        Output folder       :       {}
        Poolsize            :       {} Workers
        Buffer Size         :       {} KB
        Use random encSecKey:       {}
        Language            :       {}
        """,
        """
初始化完毕:
        歌曲/歌单/专辑ID      :        {}
        操作                  :       {}
        选项                 :       {}
        密码(Hash)           :       {}
        手机号               :       {}
        清除缓存目录         :        {}
        只进行合并           :       {}
        临时文件夹           :        {}
        输出文件夹           :       {}
        下载池大小           :       {} 线程
        缓冲区大小           :        {} KB
        采用随机encSecKey    :        {}
        语言                 :        {}
        """
    ][LANG()]
    def HELP_OPERATIONS(self): return [
        """
What to do:
    [song_audio]   download audio file only to temporay folder
    [song_lyric]   download lyrics and coverts them into lrc to temporay folder
    [song_meta]    download metadata only to temporay folder
    [song_down]    download all above,but not perfoming migration
    [song]         download all above,and perform migration
    [playlist]     parse playlist,then download every song
    [album]        download every song in album with such id
        """, 
        """
执行的操作:
    [song_audio]   仅下载音频文件到临时目录
    [song_lyric]   下载歌词并转换成 LRC 格式到输出目录
    [song_meta]    仅下载元数据到临时目录
    [song_down]    下载上述数据，但不进行整合
    [song]         下载上述数据，并进行整合
    [playlist]     下载歌单内所有歌曲并格式化
    [album]        下载专辑内所有歌曲并格式化
        """][LANG()]
    def HELP_ID(self): return ['ID of the song / playlist / album', '歌曲、歌单或专辑的 ID'][LANG()]

    def HELP_OPTIONS(self): return [
"""
Extra options
[quality_(standard, high, higher, lossless)]:Audio quality
             Specifiy download quality,e.g.[quality_lossless] will download the song in Lossless quality
             (if exsists and user's account level statisfies requirement)
""", 
"""
附加选项
[quality_(standard, high, higher, lossless)]:音频质量
    指定下载质量,如 [quality_lossless] 会尝试以无损质量下载
    （若源有如此格式且用户等级允许）
"""][LANG()]
    def HELP_TEMP_DIR(self): return ['Folder to store downloads', '临时存放下载文件的目录'][LANG()]
    def HELP_MERGE_ONLY(self): return ['Only merge audio data,skips download process.', '在临时目录中进行合并'][LANG()]

    def HELP_OUTPUT_DIR(self): return ['Folder to save', '存储保存文件的目录'][LANG()]
    def HELP_PHONE(self): return ['PHONE NUMBER of your account', '账户的手机号码'][LANG()]
    def HELP_PASSWORD(self): return ['PLAIN PASSWORD of your account', '账户的密码（明文）'][LANG()]
    def HELP_CLEAR_TEMP(self): return ['Clears the temporay folder or not', '是否删除临时文件夹'][LANG()]
    def HELP_POOLSIZE(self): return['How many download workers are summoned', '同时下载线程数目'][LANG()]
    def HELP_BUFFERSIZE(self): return['The buffer size of the downloader (in KB)', '下载缓冲区大小（单位:KB）'][LANG()]
    def HELP_RANDOM_KEYS(self): return['Whether use random encSecKeys or not', '是否采用随机 encSecKey'][LANG()]
    def HELP_LANGUAGE(self): return['Choose debug log language(ENGLISH\CHINESE)', '设定调试日志语言(ENGLISH\CHINESE)'][LANG()]
    '''------------------------------HELP STRINGS--------------------------------------'''

    def DEBUG(self): return '\033[36m' + ['[D]', '调试'][LANG()]
    def INFO(self): return '\033[1;32m' + ['[I]', '信息'][LANG()]
    def WARN(self): return '\033[33m' + ['[W]', '警告'][LANG()]
    def ERROR(self): return '\033[7;31m' + ['[E]', '错误'][LANG()]
    def DEBUG_GENERATING_KEY(self): return[
        'Generating key,this will only happen once and cost a while,please wait...','正在生成密匙，该过程将只进行 1 次，请稍后...'
    ][LANG()]
    def DEBUG_UPDATE_ACCOUNT(self): return [
        'Updating phone number and password', '更新账户信息...'][LANG()]
    def DEBUG_POSTING_LOGIN_REQUEST(self): return [
        'Posting login request with hashed passowrd:{}', '正在登录 (Hash:{})'][LANG()]
    def DEBUG_UPDATED_COOKIE(self): return [
        'Cookies updated:{}', 'Cookies 已更新:{}'][LANG()]
    def DEBUG_NEW_CSRF_TOKEN(self): return [
        'New CSRF Token:{}', 'CSRF 令牌已更新:{}'][LANG()]
    def ERROR_FAILED_TO_UPDATE_LOGIN(self): return [
        'Error updating login info:No phone number & password specified!', '未指定账号密码，更新登录信息失败！'][LANG()]
    def ERROR_LOGIN_FAILED(self): return [
        'Login Failed:{}', '登陆失败:{}'][LANG()]
    def INFO_LOGGED_IN_AS(self): return [
        'Logged in as {}', '已登录，用户名为 {}'][LANG()]
    def WARN_NOT_LOGGED_IN(self): return [
        'Have not logged in yet', '未登录'][LANG()]
    def WARN_NOT_VIP(self): return [
        'You are NOT VIP.High quality audio or VIP Only songs are not possible.', '账号无VIP等级，无法下载高音质音频或VIP独享歌曲'][LANG()]
    def INFO_VIP(self): return [
        'VIP Level Operation Possible.Procceding.', '账号含VIP等级！'][LANG()]
    def WARN_INVALID_QUALITY_CONFIG(self): return [
        'The specified Quality level {} is INVALID.Falling back to "standard"', '歌曲品质({})无效！将使用标准音质'][LANG()]
    def DEBUG_FETCHING_SONG_WITH_TOKEN(
        self): return ['Fetching song info with token:{}', '正在以令牌 ({}) 获取歌曲信息'][LANG()]
    def ERROR_FAILED_FECTCHING_SONG_WITH_TOKEN(
        self): return ['Failed Fecthing Info of Song[{}]!', '获取歌曲 (id:{}) 信息失败'][LANG()]
    def INFO_FETCHED_SONG_WITH_TOKEN(
        self): return ['Succeed in fecthing song [{}] info', '获取歌曲 (id:{}) 信息成功！'][LANG()]
    def DEBUG_FETCHING_EXTRA_SONG_INFO(
        self): return ['Fetching extra song info...', '正在获取额外数据(名称，封面，作者，专辑)...'][LANG()]
    def ERROR_FAILED_FECTCHING_EXTRA_SONG_INFO(
        self): return ['Failed Fetching extra song info:{}!', '获取额外数据({})失败'][LANG()]
    def ERROR_FAILED_FECTCHING_ALBUM_INFO(
        self): return ['Failed Fetching extra album info:{}!', '获取专辑数据({})失败'][LANG()]
    def DEBUG_FETCHING_LYRICS_WITH_TOKEN(
        self): return ['Fetching lyrics with token:{}', '正在以令牌 ({}) 获取歌词信息'][LANG()]
    def DEBUG_FETCHING_PLAYLIST_WITH_TOKEN(
        self): return ['Fetching playlist with token:{}', '正在以令牌 ({}) 获取歌单信息'][LANG()]
    def INFO_BATCH_DOWNLOAD_COMPLETE(
        self): return ['Batch download completed!', '批量下载完毕!'][LANG()]
    def INFO_FETCHED_PLAYLIST_WITH_TOKEN(
        self): return ['Playlist info fetched:{} - {}', '歌单信息已获取:{} - {}'][LANG()]
    def INFO_FETCHED_ALBUM_WITH_TOKEN(
        self): return ['Album info fetched:{} - {}', '专辑信息已获取:{} - {}'][LANG()]
    def DEBUG_FETCHING_COMMENTS_WITH_TOKEN(
        self): return ['Fetching comments with token:{}', '正在以令牌 ({}) 获取评论'][LANG()]
    def DEBUG_FETCHING_USER_PLAYLISTS_WITH_TOKEN(
        self): return ['Fetching playlists with token:{}', '正在以令牌 ({}) 获取歌单列表'][LANG()]
    def DEBUG_DOWNLOAD_STATUS(
        self): return [
        """
Downloading....{1} in queue,{2} not finished
{0}
        """,
        """
下载中，请稍后....队列中 {1} / 未完成 {2}            
{0}
        """][LANG()]
    def INFO_QUEUED_DOWNLOAD(
        self): return [
        """
Deployed task:
    {}
    → {}
        """,
        """
任务已部署:
    {}
    → {}
        """][LANG()]             
    def ERROR_FILE_MISSING(
        self): return ["File {} missing or not found!", "文件 {} 丢失或不全！"][LANG()]
    def WARN_FILE_MISSING(
        self): return ["File {} missing or not found,ignored.", "文件 {} 丢失或不全,继续执行..."][LANG()]
    def INFO_EXPORT_COMPLETE(
        self): return ["Export complete:{}", "导出成功:{}"][LANG()]

    def WARN_CLEARING_TEMP(self): return [
        'Clearing the temporay folder {}!', '删除临时文件夹 {}!'
    ][LANG()]
    def ERROR_INVALID_OPERATION(self): return [
        'Invalid operation:{}', '无效操作:{}'][LANG()]

    def DEBUG_RESPONSE(self): return ['Response:{}', '回复:{}'][LANG()]


def simple_logger(*args, format=None):
    '''
        Logging system.Used in some of my other projects as well

        Initialize one in your code to act as a callback
    '''
    if format:
        level = format.__name__.split('_')[0]
        level = getattr(strings, level)(None)
        content = format(None).format(*args)

    else:
        try:
            level = args[0].__name__.split('_')[0]
            level = getattr(strings, level)(None)
            content = args[0](None) if callable(args[0]) else args
        except Exception:
            level = strings.DEBUG(None)
            content = ' '.join(args)
    log = '{}::{} {}'.format(level, time.strftime("%H:%M:%S", time.localtime()), content)
    print(log)
    open('log.txt','w+',encoding='utf-8').write(log)