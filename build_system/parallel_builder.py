#!/usr/bin/python2

from builder import Builder
from toolchain import CToolchain
from build_exceptions import BuildError
from multiprocessing import Pool, cpu_count, Manager, Value
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
    def __init__(self, target, toolchain=CToolchain(), tmpdir='objs', language='c', sources=[], includes=[]):
        super(self.__class__, self).__init__(target, toolchain, tmpdir, language, sources, includes)
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
            print 'Terminating build due to an error on:'
            print '\t', source
            self.error['status'] = True
            self.error['source'] = source

    def compile_object(self, source, flags=[]):
        if self.error['status'] is True:
            return
        return super(self.__class__, self).compile_object(source, flags)

    def compile(self, jobs=0):
        if 0 == jobs:
            jobs = cpu_count()

        print 'Using %d jobs' % (jobs, )
        self.error['status'] = False
        self.error['source'] = None
        pool = Pool(processes=jobs)
        flags = self._gen_include_flags()
        for source in self.supported_source:
            args = (source, flags)
            pool.apply_async(self.compile_object, args=args, callback=self.compile_object_done)
        pool.close()
        pool.join()
        if self.error['status'] is True:
            raise BuildError(str(self.error['source']))

    def build(self, jobs):
        try:
            self.compile(jobs)
        except BuildError as e:
            return
        self.link()
