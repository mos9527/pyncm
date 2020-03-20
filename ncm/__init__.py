from .strings import simple_logger,strings
def Depercated(func):
    def wrapper(*args,**kwargs):
        simple_logger(func.__name__,format=strings.WARN_METHOD_DEPERCATED)
        return func(*args,**kwargs)
    return wrapper