#!/usr/bin/python2

from shell_command import ShellCommand
from source import SourceFile
from multiprocessing import Manager
import os


class Target(object):
    def __init__(self, name, sources=None, includes=None):
        self.name = name
        self.sources = [] if sources is None else sources
        self.cflags = []
        self.ldflags = []
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

    def add_ldflag(self, flag):
        if not flag in self.ldflags:
            self.ldflags += [flag]

    def remove_ldflag(self, flag):
        if flag in self.ldflags:
            self.ldflags.remove(flag)

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
        if source.is_newer(obj) is False:
            return {'source': source, 'status': 'skipped'}
        flags = [] if flags is None else flags
        include = self._gen_include_flags()
        flags = [source.path, '-c'] + include + self.cflags + flags + ['-o', obj]
        cmd = ShellCommand(compiler, flags)
        code, output = cmd.run(verbose=builder.verbose)
        if 0 == code:
            status = 'success'
            self.objects += [obj]
        else:
            status = 'failed'
        return {'source': source, 'status': status, 'output': output}

    def final(self, builder):
        raise NotImplementedError()


class Executable(Target):
    def link(self, builder):
        if len(self.objects) == 0:
            return False
        compiler = builder.toolchain.compiler
        target = os.path.join(builder.tmpdir, self.name)
        flags = self.objects + self.ldflags + ['-o', target]
        cmd = ShellCommand(compiler, flags)
        builder.print_msg('LD', target)
        code, output = cmd.run(verbose=builder.verbose)
        print output.strip()
        return code == 0

    def final(self, builder):
        self.link(builder)
