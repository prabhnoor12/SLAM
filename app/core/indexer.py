
import queue
import threading
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler



class IndexWorker(threading.Thread):
    """
    IndexWorker supports incremental and real-time indexing. Optionally, it can be extended for distributed/sharded indexing.
    """
    def __init__(self, q, process_func, shard_id=None, total_shards=1, distributed_callback=None):
        super().__init__(daemon=True)
        self.q = q
        self.process_func = process_func
        self._stop_event = threading.Event()
        self._pause_event = threading.Event()
        self._pause_event.set()  # Not paused by default
        self.shard_id = shard_id
        self.total_shards = total_shards
        self.distributed_callback = distributed_callback

    def run(self):
        while not self._stop_event.is_set():
            self._pause_event.wait()  # Wait if paused
            try:
                path = self.q.get(timeout=0.5)
                if path:
                    # Sharding: Only process files assigned to this shard
                    if self.shard_id is not None and self.total_shards > 1:
                        if (hash(path) % self.total_shards) != self.shard_id:
                            self.q.task_done()
                            continue
                    self.process_func(path)
                    # Distributed callback for further scaling (e.g., notify other nodes)
                    if self.distributed_callback:
                        self.distributed_callback(path)
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
    """
    WatcherHandler supports real-time updates and incremental indexing by tracking file changes and additions.
    """
    def __init__(self, q):
        self.q = q
        self.seen = set()  # Deduplicate paths

    def on_modified(self, event):
        if not event.is_directory:
            # Always re-index on modification for incremental updates
            self.q.put(event.src_path)
            self.seen.add(event.src_path)

    def on_created(self, event):
        if not event.is_directory:
            self.q.put(event.src_path)
            self.seen.add(event.src_path)

    def on_deleted(self, event):
        # Optionally handle deletions for real-time index cleanup
        if not event.is_directory and event.src_path in self.seen:
            self.seen.remove(event.src_path)
            # Could trigger index removal here

    def on_moved(self, event):
        # Handle file moves/renames for real-time updates
        if not event.is_directory:
            if event.src_path in self.seen:
                self.seen.remove(event.src_path)
            self.q.put(event.dest_path)
            self.seen.add(event.dest_path)