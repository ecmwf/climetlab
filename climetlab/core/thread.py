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
            if s is None:
                break
            s.execute()


class SoftThreadPool:
    def __init__(self, nthreads=4):
        self._nthreads = nthreads
        self._queue = []
        self._condition = threading.Condition()
        self._active = False
        self._lock = threading.RLock()
        self._error = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown(exc_type)

    def start(self):
        with self._lock:
            self._active = True
            for _ in range(self._nthreads):
                SoftThread(self._queue, self._condition).start()

    def shutdown(self, error=None):
        with self._lock:
            if not self._active:
                return

        for _ in range(self._nthreads):
            with self._condition:
                self._queue.append(None)
                self._condition.notify_all()

        with self._lock:
            self._active = False
            self._error = error

    def submit(self, func, *args, **kwargs):  # submit
        with self._lock:
            if not self._active:
                self.start()

        with self._condition:
            s = Future(func, args, kwargs)
            self._queue.append(s)
            self._condition.notify_all()
            return s

    def __call__(self):
        with self._lock:
            if self._error:
                raise self._error
