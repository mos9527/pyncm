'''
@Author: greats3an
@Date: 2019-08-24 18:48:46
@LastEditors: greats3an
@LastEditTime: 2019-09-01 07:13:22
@Description: CLI(command-line-interface) based chart.Something i've also used in some of my projects.
'''

import os
class CLISheet():
    '''
        Pretty sheet in CLI

        Initalize with something like this:

            CLISheet(('ROW 1',20),('ROW 2',20))
        Use it this way:

            >>CLISheet.add_line(('ROW 1','COLOMN 1'),('ROW 2','COLOUM 2'))
            0           
            >>CLISheet.modify_line(('ROW 1','CONTENT HERE LADS'),pos=0)
            >>print(CLISheet())
                       ROW 1                   ROW 2

                    CONTENT HERE LADS         COLOUM 2
    '''

    def __init__(self, *args, v_interper=' ', h_interper=' ', filler=' '):
        self.rows = [{"name": arg[0], "width":arg[1]} for arg in args]
        self.v_interper = v_interper
        self.h_interper = h_interper
        self.filler = filler
        self.columns = []

    def jstr(self, string, length):
        string = str(string)
        if(len(string) <= length):
            return string.center(length, self.filler)
        # 字串过长
        string = '>' + string[(len(string) - length) + 1:len(string)]
        return string

    def modify_line(self, *args, pos=0):
        widths = {}

        for row in self.rows:
            widths[row["name"]] = row["width"]

        for arg in args:
            if(arg[0] in self.columns[pos].keys()):
                width = widths[arg[0]]
                self.columns[pos][arg[0]] = self.jstr(str(arg[1]), width)

    def add_line(self, *args):
        new_column = {}
        widths = {}

        for row in self.rows:
            widths[row["name"]] = row["width"]
            new_column[row["name"]] = self.filler.center(
                widths[row["name"]], self.filler)

        for arg in args:
            if(arg[0] in new_column.keys()):
                width = widths[arg[0]]
                new_column[arg[0]] = self.jstr(str(arg[1]), width)

        self.columns.append(new_column)
        return len(self.columns) - 1
        # 返回该行的位置

    def remove_line(self, pos):
        self.columns[pos] = None

    def get_output(self):
        '''
            Generates the output
        '''
        width = 1
        for row in self.rows:
            width += row["width"] + 1
        # Max width
        message = self.repeat(self.h_interper, width) + '\n' + self.v_interper
        for row in self.rows:
            message += row["name"].center(row["width"],
                                          self.filler)[:row["width"]] + self.v_interper
        message += '\n' + self.repeat(self.h_interper, width) + '\n'
        # Sheet header
        for column in self.columns:
            message += self.v_interper
            for row in self.rows:
                message += column[row["name"]] + self.v_interper
            message += '\n' + self.repeat(self.h_interper, width) + '\n'
        # Sheet content
        return message

    def repeat(self, char, count):
        return char * count

    def __call__(self):
        return self.get_output()
