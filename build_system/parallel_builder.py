#!/usr/bin/python2

from builder import Builder
from toolchain import CToolchain
from build_exceptions import BuildError
from multiprocessing import Pool, cpu_count, Manager
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


class ParallelBuilder(Builder):
    def __init__(self, targets, toolchain=CToolchain(), tmpdir='objs', language='c'):
        super(self.__class__, self).__init__(targets, toolchain, tmpdir, language)
        manager = Manager()
        self.objects = manager.list()
        self.error = manager.dict()
        self.error['status'] = False
        self.error['source'] = None

    def compile_object_done(self, arg):
        if arg is None:
            return
        source, ret = arg
        if ret is False:
            self.error['status'] = True
            self.error['source'] = source

    def compile_object(self, target, source, flags=None):
        if self.error['status'] is True:
            return
        return target.compile_object(self, source, flags)

    def compile(self, jobs=0):
        if 0 == jobs:
            jobs = cpu_count()

        self.print_msg('BS', 'Using %d jobs' % (jobs, ))
        self.error['status'] = False
        self.error['source'] = None
        for target in self.targets:
            self.print_msg('BS', 'Building target %s' % target.name)
            pool = Pool(processes=jobs)
            for source in target.sources:
                args = (target, source, None)
                pool.apply_async(self.compile_object, args=args, callback=self.compile_object_done)
            pool.close()
            pool.join()
            self.run_prefinal(target)
            target.final(self)
        if self.error['status'] is True:
            raise BuildError(str(self.error['source']))