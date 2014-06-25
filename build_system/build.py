#!/usr/bin/python2

from build_system.source import SourceDirectory
from build_system.builder import Builder
from build_system.toolchain import Toolchain


def main():
    sources = SourceDirectory('sample_c', 'c').discover()
    print sources
    #mips = Toolchain(prefix='/opt/mips-2013.11/bin/mips-linux-gnu-')
    builder = Builder(target='main', sources=sources, tmpdir='/tmp')
    builder.compile()
    builder.link()
    builder.target = '/tmp/main2'
    builder.compile_link()

if '__main__' == __name__:
    main()
