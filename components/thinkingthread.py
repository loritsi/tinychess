import threading

class BackgroundTask:
    def __init__(self, func, *args, **kwargs):
        self.func = func
        self.args = args
        self.kwargs = kwargs
        self._done = False
        self._result = None
        self._thread = threading.Thread(target=self._run)
        self._thread.daemon = True
        self._thread.start()

    def _run(self):
        self._result = self.func(*self.args, **self.kwargs)
        self._done = True

    @property
    def done(self):
        return self._done

    def result(self):
        if not self._done:
            raise Exception("task not finished yet")
        return self._result


