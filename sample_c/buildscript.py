#!/usr/bin/python2

from build_system.source import SourceDirectory
from build_system.builder import Builder


sources = SourceDirectory('src', 'c').discover()
builder = Builder(target='main', sources=sources, tmpdir='objs', includes='include')
builder.add_cflag('-mtune=generic')
builder.add_cflag('-march=x86-64')
