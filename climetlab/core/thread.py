import logging
import threading

LOG = logging.getLogger(__name__)


class Future:
    def __init__(self, func, args, kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._condition = threading.Condition()
        self._ready = False
        self._result = None

    def execute(self):
        try:
            self._result = self.func(*self.args, **self.kwargs)
        except Exception as e:
            LOG.error(e)
            self._result = e
        with self._condition:
            self._ready = True
            self._condition.notify_all()

    def result(self):
        with self._condition:
            while not self._ready:
                self._condition.wait()
        if isinstance(self._result, Exception):
            raise self._result
        return self._result


class SoftThread(threading.Thread):
    def __init__(self, queue, condition):
        super().__init__(daemon=True)
        self._queue = queue
        self._condition = condition

    def run(self):
        while True:
            with self._condition:
                while len(self._queue) == 0:
                    self._condition.wait()
                s = self._queue.pop(0)
                self._condition.notify_all()
            s.execute()


class SoftThreadPool:
    def __init__(self, nthreads=4):
        self._queue = []
        self._condition = threading.Condition()
        for _ in range(nthreads):
            SoftThread(self._queue, self._condition).start()

    def submit(self, func, *args, **kwargs):  # submit
        with self._condition:
            s = Future(func, args, kwargs)
            self._queue.append(s)
            self._condition.notify_all()
            return s
