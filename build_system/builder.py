#!/usr/bin/python2

from toolchain import Toolchain
from shell_command import ShellCommand
import os


class Builder(object):
    def __init__(self, target, toolchain=Toolchain(), sources=[], tmpdir='', language='c'):
        self.target = target
        self.toolchain = toolchain
        self.sources = sources
        self.tmpdir = tmpdir
        self.language = language
        self.objects = []

    @property
    def supported_source(self):
        return filter(lambda x: self.toolchain.language == x.language, self.sources)

    def compile(self):
        compiler = self.toolchain.compiler
        for source in self.supported_source:
            obj = os.path.join(self.tmpdir, source.filename.replace(source.extension, 'o'))
            cmd = ShellCommand(compiler, [source.path, '-c', '-o', obj])
            print cmd.command
            print cmd.run()
            self.objects += [obj]

    def link(self):
        linkder = self.toolchain.linker
        target = os.path.join(self.tmpdir, self.target)
        flags = self.objects
        flags += ['-o']
        flags += [target]
        cmd = ShellCommand(linkder, flags)
        print cmd.command
        print cmd.run()

