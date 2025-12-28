
import queue
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class IndexWorker(threading.Thread):
    def __init__(self, q, process_func):
        super().__init__(daemon=True)
        self.q = q
        self.process_func = process_func
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused by default

    def run(self):
        while not self._stop_event.is_set():
            self._pause_event.wait()  # Wait if paused
            try:
                path = self.q.get(timeout=0.5)
                if path:
                    self.process_func(path)
                self.q.task_done()
            except queue.Empty:
                continue

    def stop(self):
        self._stop_event.set()

    def pause(self):
        self._pause_event.clear()

    def resume(self):
        self._pause_event.set()


class WatcherHandler(FileSystemEventHandler):
    def __init__(self, q):
        self.q = q
        self.seen = set()  # Deduplicate paths

    def on_modified(self, event):
        if not event.is_directory and event.src_path not in self.seen:
            self.q.put(event.src_path)
            self.seen.add(event.src_path)

    def on_created(self, event):
        if not event.is_directory and event.src_path not in self.seen:
            self.q.put(event.src_path)
            self.seen.add(event.src_path)