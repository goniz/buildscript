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
        self.flags = []

    @property
    def supported_source(self):
        return filter(lambda x: self.toolchain.language == x.language, self.sources)

    def add_flag(self, flag):
        if not flag in self.flags:
            self.flags += [flag]

    def remove_flag(self, flag):
        if flag in self.flags:
            self.flags.remove(flag)

    def compile(self):
        compiler = self.toolchain.compiler
        for source in self.supported_source:
            obj = os.path.join(self.tmpdir, source.filename.replace(source.extension, 'o'))
            flags = [source.path]
            flags += ['-c']
            flags += ['-mtune=generic']
            flags += ['-march=x86-64']
            flags += ['-o']
            flags += [obj]
            cmd = ShellCommand(compiler, flags)
            print cmd.command
            output = cmd.run()
            if output:
                print output
            self.objects += [obj]

    def link(self):
        compiler = self.toolchain.compiler
        target = os.path.join(self.tmpdir, self.target)
        flags = self.objects
        flags += ['-o']
        flags += [target]
        cmd = ShellCommand(compiler, flags)
        print cmd.command
        output = cmd.run()
        if output:
            print output

    def compile_link(self):
        compiler = self.toolchain.compiler
        target = os.path.join(self.tmpdir, self.target)
        flags = []
        for source in self.supported_source:
            flags += [source.path]
        flags += ['-o']
        flags += [target]
        flags += ['-v']
        cmd = ShellCommand(compiler, flags)
        print cmd.command
        output = cmd.run()
        if output:
            print output


