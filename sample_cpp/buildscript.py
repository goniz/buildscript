#!/usr/bin/python2

from build_system.source import SourceDirectory
from build_system.parallel_builder import ParallelBuilder
from build_system.toolchain import CppToolchain
from build_system.target import Executable

toolchain = CppToolchain()
sources = SourceDirectory('.', 'cpp').discover()
elf = Executable(name='main', sources=sources)
elf.add_cflag('-mtune=generic')
elf.add_cflag('-march=x86-64')

builder = ParallelBuilder(targets=[elf], toolchain=toolchain, language='cpp')
