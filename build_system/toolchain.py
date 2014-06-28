#!/usr/bin/python2

from build_exceptions import ToolchainNotFoundError
import os


class Toolchain(object):
    def __init__(self, prefix=''):
        self.prefix = prefix
        if '' != prefix and not prefix.endswith('-'):
            self.prefix += '-'

    @property
    def compiler(self):
        raise NotImplementedError()

    @property
    def linker(self):
        raise NotImplementedError()

    @property
    def assembler(self):
        raise NotImplementedError()

    @property
    def language(self):
        raise NotImplementedError()


class CToolchain(Toolchain):
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


class CppToolchain(CToolchain):
    @property
    def compiler(self):
        return self.prefix + 'g++'

    @property
    def language(self):
        return 'cpp'
