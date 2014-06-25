#!/usr/bin/python2

from toolchain import CToolchain
from shell_command import ShellCommand
import os


class Builder(object):
    def __init__(self, target, toolchain=CToolchain(), sources=[], tmpdir='objs', language='c', includes=[]):
        self.target = target
        self.toolchain = toolchain
        self.sources = sources
        self.language = language
        self.objects = []
        self.cflags = []
        self.ldflags = []
        self.tmpdir = tmpdir
        if not os.path.exists(self.tmpdir):
            os.makedirs(self.tmpdir, 0755)

        if isinstance(includes, str):
            self.includes = [includes]
        elif isinstance(includes, list):
            self.includes = includes
        else:
            raise ValueError(str(includes))

    @property
    def supported_source(self):
        return filter(lambda x: self.toolchain.language == x.language, self.sources)

    def add_cflag(self, flag):
        if not flag in self.cflags:
            self.cflags += [flag]

    def remove_cflag(self, flag):
        if flag in self.cflags:
            self.cflags.remove(flag)

    def add_ldflag(self, flag):
        if not flag in self.ldflags:
            self.ldflags += [flag]

    def remove_ldflag(self, flag):
        if flag in self.ldflags:
            self.ldflags.remove(flag)

    def __gen_include_flags(self):
        flags = map(os.path.abspath, self.includes)
        flags = ' -I'.join(flags)
        if flags:
            return ('-I' + flags).split(' ')
        return []

    def compile(self):
        compiler = self.toolchain.compiler
        for source in self.supported_source:
            obj = os.path.join(self.tmpdir, source.objectfile)
            flags = [source.path, '-c'] + self.__gen_include_flags() + self.cflags + ['-o', obj]
            cmd = ShellCommand(compiler, flags)
            print cmd.command
            output = cmd.run()
            if output:
                print output
            self.objects += [obj]

    def link(self):
        compiler = self.toolchain.compiler
        target = os.path.join(self.tmpdir, self.target)
        flags = self.objects + self.ldflags + ['-o', target]
        cmd = ShellCommand(compiler, flags)
        print cmd.command
        output = cmd.run()
        if output:
            print output

    def build(self):
        self.compile()
        self.link()