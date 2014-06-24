#!/usr/bin/python2


class Toolchain(object):
    def __init__(self, prefix=''):
        self.prefix = prefix
        if '' != prefix and not prefix.endswith('-'):
            self.prefix += '-'

    @property
    def compiler(self):
        return self.prefix + 'gcc'

    @property
    def linker(self):
        return self.prefix + 'ld'

    @property
    def assembler(self):
        return self.prefix + 'as'

    @property
    def language(self):
        return 'c'
