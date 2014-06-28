#!/usr/bin/python2

import os
import re


class SourceFile(object):
    def __init__(self, path):
        self.path = path

    @property
    def extension(self):
        regex = '\.(\w+)$'
        return re.findall(regex, self.path)[0]

    @property
    def objectfile(self):
        return self.filename.replace(self.extension, 'o')

    @property
    def filename(self):
        return os.path.basename(self.path)

    @property
    def language(self):
        ext = self.extension
        if 'c' == ext:
            return 'c'
        elif 'py' == ext:
            return 'python'
        elif 'cpp' == ext:
            return 'cpp'
        else:
            return 'Unknown'

    def __str__(self):
        return self.filename

    def __repr__(self):
        return str(self)


class SourceDirectory(object):
    def __init__(self, path, exts=None):
        self.path = path
        if isinstance(exts, str):
            self.extensions = [exts]
        elif not isinstance(exts, list):
            raise TypeError('exts should be a list of strings! got %s' % (exts, ))
        else:
            self.extensions = [] if exts is None else exts

    def add_extension(self, ext):
        if not ext in self.extensions:
            self.extensions.append(ext)

    def generate_regex(self):
        return '\.(%s)$' % ('|'.join(self.extensions), )

    def discover(self):
        regex = self.generate_regex()
        files = os.listdir(self.path)
        files = map(lambda x: os.path.join(self.path, x), files)
        files = filter(lambda x: re.findall(regex, x), files)
        return map(SourceFile, files)
