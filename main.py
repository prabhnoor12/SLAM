import sys
import queue
from PyQt6.QtWidgets import QApplication

from app.core.processor import FileProcessor
from app.core.embedding import EmbeddingEngine
from app.core.indexer import IndexWorker, WatcherHandler, Observer
from app.database.vector_db import VectorStore
from app.ui.main_window import SLAMGui
from app.utils.config import ConfigManager

class SLAMBackend:
    def __init__(self):
        # 1. Initialize core components
        self.config = ConfigManager()
        self.db = VectorStore()
        self.engine = EmbeddingEngine()
        self.proc = FileProcessor()
        
        # 2. Setup Thread-safe Queue for background indexing
        self.task_queue = queue.Queue()
        
        # 3. Start the Worker Thread (Consumer)
        # This processes files one-by-one so your CPU doesn't spike
        self.worker = IndexWorker(self.task_queue, self.handle_new_file)
        self.worker.start()

        # 4. Initialize and start the Watchdog Observer (Producer)
        self.observer = Observer()
        self.setup_watchers()
        self.observer.start()

    def setup_watchers(self):
        """Adds all folders from config to the observer."""
        handler = WatcherHandler(self.task_queue)
        watched_paths = self.config.settings.get("watched_folders", [])
        
        for path in watched_paths:
            try:
                self.observer.schedule(handler, path, recursive=True)
                print(f"[*] Now watching: {path}")
            except Exception as e:
                print(f"[!] Could not watch {path}: {e}")

    def handle_new_file(self, path):
        """The core indexing logic called by the background worker."""
        print(f"[*] Processing: {path}")
        text = self.proc.extract_text(path)
        
        if text:
            # Generate the semantic vector (AI)
            vector = self.engine.encode(text)
            
            # Store in the Vector Database
            metadata = {
                "path": str(path),
                "filename": str(path).split('/')[-1]
            }
            self.db.collection.upsert(
                ids=[str(path)], 
                embeddings=[vector.tolist()], 
                metadatas=[metadata]
            )
            print(f"[✅] Indexed: {metadata['filename']}")

if __name__ == "__main__":
    # Initialize the Qt Application
    app = QApplication(sys.argv)
    
    # Initialize the Backend Engine
    backend = SLAMBackend()
    
    # Launch the GUI
    gui = SLAMGui(backend)
    gui.show()
    
    # Standard exit procedure
    sys.exit(app.exec())