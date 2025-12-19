import threading
import time
from typing import Callable, Optional


class Scheduler:
    def __init__(self, callback: Callable[[], None], interval_seconds: int = 600):
        self.callback = callback
        self.interval = interval_seconds
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    def _run(self):
        while not self._stop_event.wait(self.interval):
            try:
                self.callback()
            except Exception:
                # swallow exceptions to keep scheduler running
                pass

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join(timeout=2)


__all__ = ["Scheduler"]
