'''
# CLI Frontend for NCMFunctions

Which sets an example to use this module.have fun ;)
'''
import logging
import coloredlogs
import colorama
from . import ncm
from pathlib import Path
import json
import os
import shutil
import sys
import argparse 

arg_whitelist = [
    'quality', 'output','temp','perserve_temp', 'pool_size', 'buffer_size', 'random_keys', 'logging_level','report_output'
]

reporters = {
    'stdout':lambda s:sys.stdout.write(s),
    'stderr':lambda s:sys.stderr.write(s),
    'logs':lambda s:logging.debug(s),
}

class ConfigProvider():
    path = os.path.join(str(Path.home()), '.pyncm')

    def __init__(self) -> None:
        self.cookies, self.logininfo, self.misc = {}, {}, {}
        # Check if config file exisits
        if os.path.isfile(ConfigProvider.path):
            # Ready to parse
            self.load()
        else:
            # Ignored.
            pass
        
    def load(self):
        # Load saved settings
        with open(ConfigProvider.path, 'r+', encoding='utf-8') as cfg:
            config = json.loads(cfg.read())
            for key in config.keys():
                setattr(self, key, config[key])
        logging.debug('Loaded config file')

    def save(self):
        # Rewrite the config file with local settings
        with open(ConfigProvider.path, 'w', encoding='utf-8') as cfg:
            cfg.write(json.dumps(
                {
                    'cookies': self.cookies,
                    'logininfo': self.logininfo,
                    'misc': self.misc
                }
            ))
        logging.debug('Saved config file')

    def destroy(self):
        # Deletes the config
        if os.path.isfile(ConfigProvider.path):os.remove(ConfigProvider.path)
        logging.warning('Destroyed config file')

colorama.init()
logging.getLogger("urllib3").setLevel(logging.WARNING)
# Set logging level for `urllib3`
parser = argparse.ArgumentParser(
    description='NCM All-in-One Downloader for python', formatter_class=argparse.RawTextHelpFormatter)
# Parser begin----------------------------------------------------------------------------
parser.add_argument('operation', metavar='OPERATION',
                    help='''What to do:
[song_audio]   download audio file only to temporay folder
[song_lyric]   download lyrics and coverts them into lrc to temporay folder
[song_meta]    download metadata only to temporay folder
[song_down]    download all above,but not perfoming migration
[song]         download all above,and merge them together
[playlist]     download every song in playlist
[album]        download every song in album
[config]       save some of the arguments,cookies,etc and do nothing else
[reset]        reset the config file and cookies
[viewcfg]      output the current config file as JSON to stdout        
               argument whitelist: --''' + ' --'.join(arg_whitelist))
parser.add_argument('--id', metavar='ID',
                    help='''ID of the song / playlist / album''', default=-1)
parser.add_argument('--quality', type=str, default='lossless',
                    help='''Audio quality
    Specifiy download quality,e.g.[lossless] will download the song in Lossless quality
    (if exsists and user's account level statisfies requirement)
    only [standard, higher, lossless] are accepted''')
parser.add_argument('--temp', type=str, default='temp',
                    help='''Folder to store downloads''')
parser.add_argument('--output', type=str, default='output',
                    help='''Folder to store all your output''')
parser.add_argument('--phone', type=str,
                    help='''Phone number of your account''', default='')
parser.add_argument('--password', type=str,
                    help='''Password of your account''', default='')
parser.add_argument('--merge-only', action='store_true',
                    help='''Only merge the downloaded stuff''')
parser.add_argument('--perserve-temp', action='store_true',
                    help='''Perserve (do not delete) the temp folder afterwards''')
parser.add_argument('--pool-size', type=int, default=4,
                    help='''Download pool size''')
parser.add_argument('--buffer-size', type=int, default=256,
                    help='''Download buffer size (KB)''')
parser.add_argument('--random-keys', action='store_true',
                    help='''Use random AES key for encryption''')
parser.add_argument('--logging-level', type=int, default=logging.DEBUG,
                    help='''Logging Level,see the following list for help
50 FATAL
40 ERROR
30 WARN
20 INFO
10 DEBUG (default)
The logs are always ouptuted to stderr
''')
parser.add_argument('--report-output', type=str,default='stderr',
                    help='''Where to output the report
stdout Output to stdout
stderr Output to stderr
logs   Output via logging.debug''')
args = parser.parse_args()
args = args.__dict__

modified = [arg[2:].replace('-','_') for arg in sys.argv if arg[:2] == '--']
# Actual modifed arguments

if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(2)

# region Loading Config & Arguments
config = ConfigProvider()  # for saved configs

operation, id, quality,  temp, output, phone, password, merge_only, perserve_temp,  pool_size, buffer_size, random_keys, logging_level,report_output = args.values()
# Parser end----------------------------------------------------------------------------

if config.misc:
    # load saved arguments form config
    for k, v in config.misc.items():
        if not k in modified:locals()[k] = v
        # ignore user set arguments        
    coloredlogs.install(level=logging_level)
else:
    coloredlogs.install(level=logging_level)

# once the arguments are parsed, do our things
logging.debug('''Initalized with the following settings:
    ID                  :       {}
    Operation           :       {}
    Option              :       {}
    Password Hash       :       {}
    Phone               :       {}
    Do perserve temp    :       {}
    Do merge only       :       {}
    Temporay folder     :       {}
    Output folder       :       {}
    Poolsize            :       {} Workers
    Buffer Size         :       {} KB
    Use random encSecKey:       {}
    Logging Level       :       {}
    Report Output       :       {}'''.format(
    id, operation, quality, ncm.ncm_core.NeteaseCloudMusicKeygen.generate_hash(
        '', password) if password else '',
    phone, perserve_temp, merge_only, temp, output, pool_size, buffer_size,
    random_keys, logging_level,report_output))

ncmfunc = ncm.ncm_func.NCMFunctions(
    temp, output, merge_only, pool_size, buffer_size, random_keys,reporters[report_output])


if config.cookies:
    # Load cookies if applicable
    try:
        ncm.session.cookies.update(config.cookies)
        logging.debug('Loaded stored cookies')
    except Exception as e:
        logging.error('Failed to load stored cookies:%s' % e)

if config.logininfo:
    # Load login info if applicable
    ncmfunc.NCM.login_info = config.logininfo
    if ncmfunc.NCM.login_info['success']:
        logging.debug('Loaded last login info (logged in as %s)' % ncmfunc.NCM.login_info['content']['profile']['nickname'])

# endregion

if phone and password:
    # passport provided,login with them
    ncmfunc.Login(phone, password)

'''
    Reflect the operations to certain functions
'''


def NoExecWrapper(func, *args, **kwargs):
    '''
        Wrapper that treats functions like a variable then returns them
    '''
    def wrapper():
        func(*args, **kwargs)
    return wrapper


def SaveConfig():
    # Saving cookies
    config.cookies = ncm.session.cookies.get_dict()
    # Saving logininfo
    config.logininfo = ncmfunc.NCM.login_info
    # Saving filtered arguments
    config.misc = {k: v for k, v in args.items() if k in arg_whitelist}
    config.save()
    sys.exit(0)


reflection = {
    'viewcfg':lambda:print(open(ConfigProvider.path, 'r+', encoding='utf-8').read()),
    'reset':config.destroy,
    'config': SaveConfig,
    'song_audio': NoExecWrapper(ncmfunc.DownloadTrackAudio, id=id, quality=quality),
    'song_lyric':   NoExecWrapper(ncmfunc.DownloadAndFormatLyrics, id=id),
    'song_meta': NoExecWrapper(ncmfunc.DownloadTrackInfo, id=id),
    'song_down': NoExecWrapper(ncmfunc.DownloadAll, id=id, quality=quality),
    'song':  NoExecWrapper(ncmfunc.DownloadAllAndMerge, id=id, quality=quality),
    'playlist': NoExecWrapper(ncmfunc.DownloadAllTracksInPlaylistAndMerge, id=id, quality=quality, merge_only=merge_only),
    'album': NoExecWrapper(ncmfunc.DownloadAllTracksInAlbumAndMerge, id=id, quality=quality, merge_only=merge_only)
}

if not operation in reflection.keys():
    logging.error('Invalid operation:%s' % operation)
else:
    try:
        result = reflection[operation]()
        logging.info(f'Sucessfully executed {operation}')
    except Exception as e:
        logging.error(f'Error while executing "{operation}" : {e}')
        # Print out traceback
        import traceback
        traceback.print_stack(file=sys.stderr)
        # Exit with status code 1
        sys.exit(1)

if not perserve_temp and os.path.isdir(temp):
    # Clears temporay folder if we dont want to save it
    logging.debug('Clearing temp folder:%s' % temp)
    shutil.rmtree(temp)
# Quits gracefuly
sys.exit(0)