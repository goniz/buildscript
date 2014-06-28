#!/usr/bin/python2

from builder import Builder
from toolchain import CToolchain
from build_exceptions import BuildError
from multiprocessing import Pool, cpu_count, Manager
from termcolor import colored
import copy_reg
import types


def _pickle_method(method):
    func_name = method.im_func.__name__
    obj = method.im_self
    cls = method.im_class
    return _unpickle_method, (func_name, obj, cls)


def _unpickle_method(func_name, obj, cls):
    for cls in cls.mro():
        try:
            func = cls.__dict__[func_name]
        except KeyError:
            pass
        else:
            break
    return func.__get__(obj, cls)

copy_reg.pickle(types.MethodType, _pickle_method, _unpickle_method)

SINGLE_OBJECT_TIMEOUT = 25


class ParallelBuilder(Builder):
    def __init__(self, targets, toolchain=CToolchain(), tmpdir='objs', language='c'):
        super(self.__class__, self).__init__(targets, toolchain, tmpdir, language)
        manager = Manager()
        self.objects = manager.list()
        self.results = manager.Queue()

    def compile_object_done(self, arg):
        if arg is None:
            return
        self.results.put_nowait(arg)

    def compile_object(self, target, source, flags=None):
        return target.compile_object(self, source, flags)

    def _wait_for_compilation(self, target):
        count = 0
        while count < len(target.sources):
            retval = self.results.get(True, SINGLE_OBJECT_TIMEOUT)
            if retval['status'] is False:
                self.print_msg('CC', colored(retval['source'].filename, 'red'))
            else:
                self.print_msg('CC', retval['source'].filename)
            count += 1
            if retval['status'] is False:
                raise BuildError(retval['output'])

    def compile(self, jobs=0):
        if 0 == jobs:
            jobs = cpu_count()

        self.print_msg('BS', 'Using %s parallel job(s)' % colored(str(jobs), 'yellow'))
        for target in self.targets:
            self.print_msg('BS', 'Building target %s' % colored(target.name, 'yellow'))
            pool = Pool(processes=jobs)
            for source in target.sources:
                args = (target, source, None)
                pool.apply_async(self.compile_object, args=args, callback=self.compile_object_done)
            pool.close()
            self._wait_for_compilation(target)
            pool.join()
            self.run_prefinal(target)
            target.final(self)
