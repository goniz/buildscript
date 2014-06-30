#!/usr/bin/python2

from build_exceptions import BuildError
import os
import re


class File(object):
    def __init__(self, path):
        self.path = path

    def is_newer(self, other):
        if os.path.exists(other) is False:
            return True
        if os.path.exists(self.path) is False:
            raise BuildError('SourceFile.path does not exists??')

        obj = os.stat(other).st_ctime
        me = os.stat(self.path).st_ctime
        if me > obj:
            return True
        return False

    @property
    def extension(self):
        regex = '\.(\w+)$'
        return re.findall(regex, self.path)[0]

    @property
    def filename(self):
        return os.path.basename(self.path)

    def __str__(self):
        return self.filename

    def __repr__(self):
        return str(self)


class Directory(object):
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

    def discover(self, output=File):
        regex = self.generate_regex()
        files = os.listdir(self.path)
        files = map(lambda x: os.path.join(self.path, x), files)
        files = filter(lambda x: re.findall(regex, x), files)
        return map(output, files)


class SourceFile(File):
    @property
    def objectfile(self):
        return self.filename.replace(self.extension, 'o')

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


class SourceDirectory(Directory):
    def discover(self, output=SourceFile):
        return super(self.__class__, self).discover(output)