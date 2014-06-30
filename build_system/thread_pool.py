#!/usr/bin/python2

from Queue import Queue
from threading import Thread


class Worker(Thread):
    """Thread executing tasks from a given tasks queue"""
    def __init__(self, tasks):
        super(self.__class__, self).__init__()
        self.tasks = tasks
        self.daemon = True
        self.start()

    def run(self):
        while True:
            func, args, kargs = self.tasks.get()
            if func is None:
                #None func is a sign to exit
                self.tasks.task_done()
                return

            try:
                ret = func(*args)
                if kargs and 'callback' in kargs:
                    kargs['callback'](ret)
            except Exception as e:
                print type(e), e
            finally:
                self.tasks.task_done()


class ThreadPoolState(object):
    IDLE = 1
    CLOSED = 2
    WAIT_JOIN = 3


class ThreadPoolError(Exception):
    pass


class ThreadPool(object):
    """Pool of threads consuming tasks from a queue"""
    def __init__(self, workers):
        self.tasks = Queue()
        self.workers = [Worker(self.tasks) for x in xrange(workers)]
        self.state = ThreadPoolState.IDLE

    def apply_async(self, func, args, **kargs):
        """Add a task to the queue"""
        if self.state != ThreadPoolState.IDLE:
            raise ThreadPoolError('ThreadPool cant accept any more tasks')
        self.tasks.put((func, args, kargs))

    def close(self):
        self.state = ThreadPoolState.CLOSED
        while not self.tasks.empty():
            self.tasks.get_nowait()
            self.tasks.task_done()
        for worker in self.workers:
            self.tasks.put((None, (), {}))

    def join(self):
        """Wait for completion of all the tasks in the queue"""
        self.state = ThreadPoolState.WAIT_JOIN
        self.tasks.join()
