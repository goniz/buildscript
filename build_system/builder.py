#!/usr/bin/python2

from toolchain import CToolchain
from build_exceptions import BuildError
from datetime import datetime, timedelta
from termcolor import cprint, colored
import os
import sys
import shutil


class Builder(object):
    def __init__(self, targets=None, toolchain=CToolchain(), tmpdir='objs', language='c'):
        self.targets = [] if targets is None else targets
        self.toolchain = toolchain
        self.language = language
        self.verbose = False
        self.tmpdir = tmpdir
        self.prebuild = []
        self.postbuild = []
        self.prefinal = []
        self.statistics = {'externals': timedelta(0), 'compile': timedelta(0)}
        self.clean(clean=False)

    def print_msg(self, tag, msg, newline=True):
        tag = colored('[' + tag + ']', 'green')
        newline = '\n' if newline is True else ''
        self.print_output('%s  %s%s' % (tag, msg, newline))

    @staticmethod
    def print_output(msg):
        sys.stdout.write(msg)
        sys.stdout.flush()

    def compile(self, jobs=1):
        for target in self.targets:
            self.print_msg('BS', 'Building target %s' % colored(target.name, 'yellow'))
            for source in target.sources:
                retval = target.compile_object(self, source)
                if retval['status'] == 'success':
                    self.print_msg('CC', source.filename)
                if retval['status'] == 'failed':
                    raise BuildError(retval['output'])
            self.run_prefinal(target)
            target.final(self)
        return True

    def run_prebuild(self):
        start = datetime.now()
        for prebuild in self.prebuild:
            prebuild(self)
        end = datetime.now()
        self.statistics['externals'] += (end - start)

    def run_prefinal(self, target):
        start = datetime.now()
        for prefinal in self.prefinal:
            prefinal(self, target)
        end = datetime.now()
        self.statistics['externals'] += (end - start)

    def run_postbuild(self):
        start = datetime.now()
        for postbuild in self.postbuild:
            postbuild(self)
        end = datetime.now()
        self.statistics['externals'] += (end - start)

    def _get_execution_time(self, key='total'):
        if 'total' == key:
            delta = self.statistics['externals'] + self.statistics['compile']
        else:
            delta = self.statistics[key]
        if 0 == delta.seconds:
            time = '%d.%06d' % (delta.seconds, delta.microseconds)
        else:
            time = str(delta.total_seconds())
        return time + ' sec'

    def print_statistics(self):
        print 'Build Statistics:'
        print '\tCompile time:\t\t%s' % self._get_execution_time('compile')
        print '\tExternal callbacks:\t%s' % self._get_execution_time('externals')
        print '\tTotal time:\t\t%s' % colored(self._get_execution_time(), 'yellow')

    def build(self, jobs):
        self.run_prebuild()
        start = datetime.now()
        try:
            self.compile(jobs)
        except BuildError as e:
            cprint('\nTerminating build due to an error on:', 'red')
            cprint(e, 'red')
            return
        finally:
            end = datetime.now()
            self.statistics['compile'] += (end - start)

        self.run_postbuild()
        self.print_statistics()

    def clean(self, clean=True):
        if clean is True:
            self.print_msg('BS', 'Cleaning')
            shutil.rmtree(self.tmpdir)
        if os.path.exists(self.tmpdir) is False:
            os.makedirs(self.tmpdir, 0755)


