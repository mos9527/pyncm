'''
@Author: greats3an
@Date: 2020-02-09 18:03:29
@LastEditors  : greats3an
@LastEditTime : 2020-02-10 19:20:21
@Site: mos9527.tooo.top
@Description: file content
'''
'''
    Simple progress bar for console
    by 'Carlos Alexandre S. da Fonseca'
    modified to fit the purpose better
'''
from __future__ import print_function
import sys



class ProgressBar(object):
    """
    Create terminal progress bar

        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        nonfill     - Optional  : bar fill when no value is specified (Str)
        zfill       - Optional  : bar zero fill character (Str)
        file        - Optional  : output file (Stream)
    """
    def __init__(self, total, prefix='', suffix='', decimals=1, length=40, nonfill='=',fill='#', zfill='-', file=sys.stdout):
        self.__prefix = prefix
        self.__suffix = suffix
        self.__decimals = decimals
        self.__length = length
        self.__fill = fill
        self.__nonfill = nonfill
        self.__zfill = zfill
        self.__total = total
        self.__iteration = 0
        self.__file = file

    def __call__(self, iteration):
        """
        Create and return the progress bar string

            iteration   - Required  : current iteration (Int)
        """
        if self.__total and (iteration or iteration == 0):
            percent = ("{0:." + str(self.__decimals) + "f}")
            percent = percent.format(100 * (iteration / float(self.__total)))
            filled_length = int(self.__length * iteration // self.__total)
            pbar = self.__fill * filled_length + self.__zfill * (self.__length - filled_length)
            return '{0} |{1}| {2}% {3}'.format(self.__prefix, pbar, percent, self.__suffix)
        else:
            filled_length = int(self.__length)
            pbar = str(iteration).center(self.__length,self.__nonfill) + self.__zfill * (self.__length - filled_length)
            return '{0} |{1}| {2}% {3}'.format(self.__prefix, pbar, 'NaN', self.__suffix)            