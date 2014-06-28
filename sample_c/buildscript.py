#!/usr/bin/python2

from build_system.source import SourceDirectory
from build_system.builder import Builder
from build_system.target import Executable


sources = SourceDirectory('src', 'c').discover()
elf = Executable(name='main', sources=sources, includes='include')
elf.add_cflag('-mtune=generic')
elf.add_cflag('-march=x86-64')

builder = Builder(targets=[elf])
