#!/usr/bin/python2

from toolchain import CToolchain
from shell_command import ShellCommand
from source import SourceFile
from build_exceptions import BuildError
import os


class Builder(object):
    def __init__(self, target, toolchain=CToolchain(), tmpdir='objs', language='c', sources=[], includes=[]):
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

    def add_source(self, source):
        if not isinstance(source, SourceFile):
            return
        if not source in self.sources:
            self.sources.append(source)

    def add_sources(self, sources):
        for source in sources:
            self.add_source(source)

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

    def _gen_include_flags(self):
        flags = map(os.path.abspath, self.includes)
        flags = ' -I'.join(flags)
        if flags:
            return ('-I' + flags).split(' ')
        return []

    def compile_object(self, source, flags=[]):
        compiler = self.toolchain.compiler
        obj = os.path.join(self.tmpdir, source.objectfile)
        flags = [source.path, '-c'] + flags + self.cflags + ['-o', obj]
        cmd = ShellCommand(compiler, flags)
        print ' [CC]  %-20s\t-->\t%s' % (source.filename, source.objectfile)
        try:
            cmd.run(verbose=False)
            self.objects += [obj]
            return source, True
        except ValueError as e:
            print e
            return source, False

    def compile(self):
        flags = self._gen_include_flags()
        for source in self.supported_source:
            source, ret = self.compile_object(source, flags)
            if ret is False:
                raise BuildError(str(source))
        return True

    def link(self):
        compiler = self.toolchain.compiler
        target = os.path.join(self.tmpdir, self.target)
        flags = self.objects + self.ldflags + ['-o', target]
        cmd = ShellCommand(compiler, flags)
        try:
            cmd.run(verbose=True)
            return True
        except ValueError as e:
            print e
            return False

    def build(self, jobs):
        try:
            self.compile()
        except BuildError as e:
            print 'Terminating build due to an error on:'
            print '\t', e
            return
        self.link()