#!/usr/bin/python2

from builder import Builder
from toolchain import CToolchain
from build_exceptions import BuildError
from multiprocessing import cpu_count
from Queue import Queue
from thread_pool import ThreadPool
from termcolor import colored

SINGLE_OBJECT_TIMEOUT = 25


class ParallelBuilder(Builder):
    def __init__(self, targets, toolchain=CToolchain(), tmpdir='objs', language='c'):
        super(self.__class__, self).__init__(targets, toolchain, tmpdir, language)
        self.objects = list()
        self.results = Queue()
        self.error = False

    def compile_object_done(self, arg):
        if arg is None:
            return
        self.results.put_nowait(arg)

    def compile_object(self, target, source, flags=None):
        if self.error is True:
            return {'status': 'skipped', 'source': source}
        try:
            return target.compile_object(self, source, flags)
        except Exception as e:
            return {'status': 'failed', 'source': source, 'output': e}

    def _wait_for_compilation(self, target):
        count = 0
        while count < len(target.sources):
            retval = self.results.get(True, SINGLE_OBJECT_TIMEOUT)
            if retval['status'] == 'failed':
                self.print_msg('CC', colored(retval['source'].filename, 'red'))
                raise BuildError(retval['output'])
            elif retval['status'] == 'success':
                self.print_msg('CC', retval['source'].filename)
            count += 1

    def compile(self, jobs=0):
        if 0 == jobs:
            jobs = cpu_count()

        self.print_msg('BS', 'Using %s parallel job(s)' % colored(str(jobs), 'yellow'))
        for target in self.targets:
            self.print_msg('BS', 'Building target %s' % colored(target.name, 'yellow'))
            pool = ThreadPool(jobs)
            for source in target.sources:
                args = (target, source, None)
                pool.apply_async(self.compile_object, args=args, callback=self.compile_object_done)
            try:
                self._wait_for_compilation(target)
            except BuildError as e:
                raise
            finally:
                pool.close()
                pool.join()
            self.run_prefinal(target)
            target.final(self)
