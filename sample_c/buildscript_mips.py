#!/usr/bin/python2

from build_system.source import SourceDirectory
from build_system.builder import Builder
from build_system.toolchain import CToolchain

sources = SourceDirectory('src', 'c').discover()
toolchain = CToolchain(prefix='mips-linux-gnu-')
builder = Builder(target='main', sources=sources, tmpdir='objs', toolchain=toolchain, includes='include')
