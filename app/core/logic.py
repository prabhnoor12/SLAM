import os
import hashlib
from app.utils.diagnostics import logger, profile_performance
from abc import ABC, abstractmethod
from typing import Any, Callable, List, Dict, Generator, Optional



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

    @profile_performance
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
            chunk_ids = []
            chunk_vectors = []
            chunk_metas = []
            for i, chunk in enumerate(self.chunk_text(text)):
                vector = self.engine.encode(chunk)
                chunk_id = f"{path}_{i}"
                meta = {
                    "path": str(path),
                    "hash": current_hash,
                    "chunk_id": i
                }
                chunk_ids.append(chunk_id)
                chunk_vectors.append(vector.tolist())
                chunk_metas.append(meta)

            # 4. Commit to DB (atomic before moving file)
            if chunk_ids:
                self.db.collection.upsert(
                    ids=chunk_ids,
                    embeddings=chunk_vectors,
                    metadatas=chunk_metas
                )

            # 5. POST-PROCESSING: Archive the file
            from app.core.processor import archive_on_index
            new_path = archive_on_index(path)
            # If the path changed, update metadata in DB (optional: update in place or re-upsert)
            if new_path != path:
                for meta in chunk_metas:
                    if meta["path"] == path:
                        meta["path"] = new_path
                # Optionally, update DB with new path metadata
            logger.info(f"File archived to: {new_path}")

        except Exception as e:
            logger.error(f"Failed to process {path}: {str(e)}")
            self.dead_letter_queue.append(path)

    @profile_performance
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