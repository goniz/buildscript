#!/usr/bin/python2

from build_system.source import SourceDirectory
from build_system.shell_command import ShellCommand
from build_system.builder import Builder


def main():
    sources = SourceDirectory('sample_c', 'c').discover()
    print sources
    builder = Builder(target='main', sources=sources, tmpdir='/tmp')
    builder.compile()
    builder.link()

if '__main__' == __name__:
    main()
