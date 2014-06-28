#!/usr/bin/python2

from build_system.source import SourceDirectory
from build_system.builder import Builder
from build_system.toolchain import CToolchain
from build_system.target import Executable

sources = SourceDirectory('src', 'c').discover()
toolchain = CToolchain(prefix='/opt/mips-2013.11/bin/mips-linux-gnu-')
elf = Executable('main', sources=sources, includes='include')
builder = Builder(targets=[elf], toolchain=toolchain)
