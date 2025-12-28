import os
import hashlib
import logging
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict, Generator, Optional

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SLAM_Backend")

# --- 🧠 Logic Processor Architecture ---

class LogicProcessor(ABC):
    """Abstract Base Class for data transformation."""
    @abstractmethod
    def process(self, data: Any) -> Any:
        pass

class PipelineProcessor(LogicProcessor):
    """Handles a sequence of transformation functions (Rules/Plugins)."""
    def __init__(self, steps: List[Callable[[Any], Any]]):
        self.steps = steps

    def process(self, data: Any) -> Any:
        for step in self.steps:
            data = step(data)
        return data

class ChainedLogicProcessor(LogicProcessor):
    """Composite processor that chains multiple LogicProcessor objects."""
    def __init__(self, processors: List[LogicProcessor]):
        self.processors = processors

    def process(self, data: Any) -> Any:
        for processor in self.processors:
            data = processor.process(data)
        return data

# --- ⚙️ Main Backend ---

class SLAMBackend:
    def __init__(self, db, proc, engine, logic_processor: Optional[LogicProcessor] = None):
        self.db = db
        self.proc = proc
        self.engine = engine
        self.logic_processor = logic_processor
        
        # Internal State
        self.dead_letter_queue = []
        self._batch_cache = {"ids": [], "vectors": [], "metas": []}
        self.batch_size = 10

    def get_file_hash(self, path: str) -> str:
        """Calculates SHA-256 using memory-efficient chunking."""
        sha256 = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(8192), b""): # 8KB blocks
                sha256.update(byte_block)
        return sha256.hexdigest()

    def chunk_text(self, text: str, size: int = 1000) -> Generator[str, None, None]:
        """Generator to yield text chunks without loading all into RAM."""
        for i in range(0, len(text), size):
            yield text[i : i + size]

    def handle_new_file(self, path: str):
        if not os.access(path, os.R_OK):
            logger.error(f"Access Denied: {path}")
            self.dead_letter_queue.append(path)
            return

        try:
            # 1. Deduplication check
            current_hash = self.get_file_hash(path)
            existing = self.db.collection.get(ids=[path])
            if existing['ids'] and existing['metadatas'][0].get('hash') == current_hash:
                return 

            # 2. Extraction & Transformation
            text = self.proc.extract_text(path)
            if not text:
                return

            if self.logic_processor:
                text = self.logic_processor.process(text)

            # 3. Vectorization & Batching
            for i, chunk in enumerate(self.chunk_text(text)):
                vector = self.engine.encode(chunk)
                
                self._batch_cache["ids"].append(f"{path}_{i}")
                self._batch_cache["vectors"].append(vector.tolist())
                self._batch_cache["metas"].append({
                    "path": str(path),
                    "hash": current_hash,
                    "chunk_id": i
                })

                if len(self._batch_cache["ids"]) >= self.batch_size:
                    self.flush_batch()

        except Exception as e:
            logger.error(f"Failed to process {path}: {str(e)}")
            self.dead_letter_queue.append(path)

    def flush_batch(self):
        """Commits cached vectors to the database."""
        if not self._batch_cache["ids"]:
            return

        self.db.collection.upsert(
            ids=self._batch_cache["ids"],
            embeddings=self._batch_cache["vectors"],
            metadatas=self._batch_cache["metas"]
        )
        # Clear cache
        self._batch_cache = {"ids": [], "vectors": [], "metas": []}
        logger.info("Batch flushed to Vector DB.")

    def retry_dead_letters(self):
        """Attempts to re-process files that failed previously."""
        to_retry = list(self.dead_letter_queue)
        self.dead_letter_queue.clear()
        for path in to_retry:
            self.handle_new_file(path)