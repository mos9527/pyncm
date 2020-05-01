import logging,requests
logger = logging.getLogger('NeteaseCloudMusic')
# Logger and stuff
session = requests.Session()
# Session for requesting things
def Depercated(func):
    def wrapper(*args,**kwargs):
        logger.warn('Deprecated method `%s` is being called,please,avoid using it since it will possibly be removed' % func.__name__)
        return func(*args,**kwargs)
    return wrapper
import os
__all__ = [i[:-3] for i in os.listdir(os.path.dirname(__file__)) if i[-2:] == 'py' and i != '__init__.py']
from . import *