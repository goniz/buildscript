#!/usr/bin/python2

from build_system.source import SourceDirectory
from build_system.builder import Builder
from build_system.toolchain import CppToolchain

toolchain = CppToolchain()
sources = SourceDirectory('.', 'cpp').discover()
builder = Builder(target='main', sources=sources, tmpdir='objs', toolchain=toolchain)
builder.add_cflag('-mtune=generic')
builder.add_cflag('-march=x86-64')
