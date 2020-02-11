# coding: utf-8
'''
@Author: greats3an
@Date: 2020-01-24 11:32:51
@LastEditors  : greats3an
@LastEditTime : 2020-02-11 16:51:33
@Site: mos9527.tooo.top
@Description: CLI Interface for most functions
'''
import argparse,sys,shutil
from ncm.ncm_core import NeteaseCloudMusicKeygen
from ncm.ncm_func import NCMFunctions
from ncm.strings import strings, simple_logger
log = simple_logger

parser = argparse.ArgumentParser(
    description='NCM All-in-One Downloader for python', formatter_class=argparse.RawTextHelpFormatter)

print(strings.INIT_INIT(None))
# Parser begin----------------------------------------------------------------------------
parser.add_argument('operation', metavar='OPERATION',
                    help=strings.HELP_OPERATIONS(None))
parser.add_argument('id', metavar='ID', help=strings.HELP_ID(None))
parser.add_argument('--opt', type=str, default='quality_lossless',
                    help=strings.HELP_OPTIONS(None))
parser.add_argument('--temp', type=str, default='temp',
                    help=strings.HELP_TEMP_DIR(None))
parser.add_argument('--output', type=str, default='output',
                    help=strings.HELP_OUTPUT_DIR(None))
parser.add_argument('--phone', type=str, help=strings.HELP_PHONE(None),default='')
parser.add_argument('--password', type=str, help=strings.HELP_PASSWORD(None),default='')
parser.add_argument('--merge-only', action='store_true',
                    help=strings.HELP_MERGE_ONLY(None))
parser.add_argument('--clear-temp', action='store_true',
                    help=strings.HELP_CLEAR_TEMP(None))
parser.add_argument('--pool-size', type=int, default=4,
                    help=strings.HELP_POOLSIZE(None))
parser.add_argument('--buffer-size', type=int, default=256,
                    help=strings.HELP_BUFFERSIZE(None))
parser.add_argument('--random-keys', action='store_true',
                    help=strings.HELP_RANDOM_KEYS(None))
if len(sys.argv) < 2:
    parser.print_help()
    sys.exit(2)
args = parser.parse_args()
args = args.__dict__

operation, id, opt,  temp, output, phone, password, merge_only, clear_temp,  pool_size, buffer_size, random_keys = args.values()
# Parser end----------------------------------------------------------------------------
log(id, operation, opt, NeteaseCloudMusicKeygen.generate_hash('',password) , phone, clear_temp, merge_only, temp, output,
    pool_size, buffer_size, random_keys, format=strings.INIT_INITALIZED_WITH_ARGS)
ncm = NCMFunctions(temp, output, merge_only, pool_size,
                   buffer_size, random_keys, log)
# Process login info
if phone and password:
    ncm.Login(phone, password)

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


reflection = {
    'song_audio': NoExecWrapper(ncm.DownloadSongAudio, id=id, quality=opt),
    'song_lyric':   NoExecWrapper(ncm.DownloadAndFormatLyrics, id=id),
    'song_meta':  NoExecWrapper(ncm.DownloadSongInfo, id=id),
    'song_down':  NoExecWrapper(ncm.DownloadAllInfo, id=id, quality=opt),
    'song':  NoExecWrapper(ncm.DownloadAllAndMerge, id=id, quality=opt),
    'playlist': NoExecWrapper(ncm.DownloadAllSongsInPlaylistAndMerge, id=id, quality=opt, merge_only=merge_only),
    'album': NoExecWrapper(ncm.DownloadAllSongsInAlbumAndMerge, id=id, quality=opt, merge_only=merge_only)
}

if not operation in reflection.keys():
    log(operation, format=strings.ERROR_INVALID_OPERATION)
else:
    func = reflection[operation]()

if clear_temp:
    # Clears temporay folder
    log(temp, format=strings.WARN_CLEARING_TEMP)
    shutil.rmtree(temp)
