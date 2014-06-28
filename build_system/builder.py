#!/usr/bin/python2

from toolchain import CToolchain
from build_exceptions import BuildError
from datetime import datetime, timedelta
import os


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
        if not os.path.exists(self.tmpdir):
            os.makedirs(self.tmpdir, 0755)

    @staticmethod
    def print_msg(tag, msg):
        print '[%s]  %s' % (tag, msg)

    def compile(self, jobs=1):
        for target in self.targets:
            for source in target.sources:
                self.print_msg('CC', source.filename)
                source, ret = target.compile_object(self, source)
                if ret is False:
                    raise BuildError(str(source))
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

    def _get_execution_time(self, key):
        delta = self.statistics[key]
        if 0 == delta.seconds:
            time = '%d.%06d' % (delta.seconds, delta.microseconds)
        else:
            time = str(delta.total_seconds()) + ' sec'
        return time + ' sec'

    def print_statistics(self):
        print '\nBuild Statistics:'
        print '\tCompile time:\t\t%s' % self._get_execution_time('compile')
        print '\tExternal callbacks:\t%s' % self._get_execution_time('externals')

    def build(self, jobs):
        self.run_prebuild()
        start = datetime.now()
        try:
            self.compile(jobs)
        except BuildError as e:
            print '\nTerminating build due to an error on:'
            print str(e)
            return
        finally:
            end = datetime.now()
            self.statistics['compile'] += (end - start)

        self.run_postbuild()
        self.print_statistics()
