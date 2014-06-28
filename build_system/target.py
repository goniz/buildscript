#!/usr/bin/python2

from source import SourceFile
from shell_command import ShellCommand
from multiprocessing import Manager
import os


class Target(object):
    def __init__(self, name, sources=None, includes=None):
        self.name = name
        self.sources = [] if sources is None else sources
        self.cflags = []
        manager = Manager()
        self.objects = manager.list()
        if isinstance(includes, str):
            self.includes = [includes]
        elif isinstance(includes, list):
            self.includes = includes
        elif includes is None:
            self.includes = []
        else:
            raise ValueError(str(includes))

    def add_source(self, source):
        if not isinstance(source, SourceFile):
            return
        if not source in self.sources:
            self.sources.append(source)

    def add_sources(self, sources):
        for source in sources:
            self.add_source(source)

    def add_cflag(self, flag):
        if not flag in self.cflags:
            self.cflags += [flag]

    def remove_cflag(self, flag):
        if flag in self.cflags:
            self.cflags.remove(flag)

    def _gen_include_flags(self):
        flags = map(os.path.abspath, self.includes)
        flags = ' -I'.join(flags)
        if flags:
            return ('-I' + flags).split(' ')
        return []

    def compile_object(self, builder, source, flags=None):
        compiler = builder.toolchain.compiler
        obj = os.path.join(builder.tmpdir, source.objectfile)
        flags = [] if flags is None else flags
        include = self._gen_include_flags()
        flags = [source.path, '-c'] + include + self.cflags + flags + ['-o', obj]
        cmd = ShellCommand(compiler, flags)
        builder.print_msg('CC', source.filename)
        try:
            cmd.run(verbose=builder.verbose)
            self.objects += [obj]
            return source, True
        except ValueError as e:
            print e
            return source, False

    def final(self, builder):
        raise NotImplementedError()


class Executable(Target):
    def __init__(self, name, sources=None, includes=None):
        super(self.__class__, self).__init__(name, sources, includes)
        self.ldflags = []

    def add_ldflag(self, flag):
        if not flag in self.ldflags:
            self.ldflags += [flag]

    def remove_ldflag(self, flag):
        if flag in self.ldflags:
            self.ldflags.remove(flag)

    def link(self, builder):
        compiler = builder.toolchain.compiler
        target = os.path.join(builder.tmpdir, self.name)
        flags = self.objects + self.ldflags + ['-o', target]
        cmd = ShellCommand(compiler, flags)
        builder.print_msg('LD', target)
        try:
            cmd.run(verbose=builder.verbose)
            return True
        except ValueError as e:
            print e
            return False

    def final(self, builder):
        self.link(builder)
