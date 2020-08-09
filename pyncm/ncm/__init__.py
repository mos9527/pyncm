import logging,requests
logger = logging.getLogger('NeteaseCloudMusic')
# Logger and stuff
session = requests.Session()
# Session for requesting things
def Depercated(replacement):
    def prewrapper(func):    
        def wrapper(*args,**kwargs):
            logger.warn('Function `%s` is depercated,and a replacement method exisits.Consider replacing it with `%s`' % (func.__name__,replacement))
            return func(*args,**kwargs)
        return wrapper
    return prewrapper
from .ncm_core import NeteaseCloudMusic,NeteaseCloudMusicKeygen
from .ncm_func import NCMFunctions
from .lrcparser import LrcParser
# Import all subclasses