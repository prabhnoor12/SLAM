import os
import hashlib
from app.core.processor import Processor
from app.core.embedding import EmbeddingEngine

class SLAMBackend:
    def __init__(self, db, proc: Processor, engine: EmbeddingEngine):
        self.db = db
        self.proc = proc
        self.engine = engine
        self.dead_letter_queue = []
        self.batch_ids = []
        self.batch_vectors = []
        self.batch_metadatas = []
        self.batch_size = 10  # Tune as needed

    def get_file_hash(self, path):
        sha256_hash = hashlib.sha256()
        with open(path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def handle_new_file(self, path):
        # 1. Check if file is still there and accessible
        if not os.access(path, os.R_OK):
            self.dead_letter_queue.append(path)
            return
        try:
            # 2. Hashing Check
            current_hash = self.get_file_hash(path)
            existing = self.db.collection.get(ids=[path])
            if existing['ids'] and existing['metadatas'][0].get('hash') == current_hash:
                return  # Skip! File content hasn't changed.

            # 3. Content Extraction
            text = self.proc.extract_text(path)
            if text:
                # 4. Chunking
                chunks = self.chunk_text(text)
                for i, chunk in enumerate(chunks):
                    vector = self.engine.encode(chunk)
                    metadata = {
                        "path": str(path),
                        "hash": current_hash,
                        "chunk_id": i
                    }
                    self.batch_ids.append(f"{path}_{i}")
                    self.batch_vectors.append(vector.tolist())
                    self.batch_metadatas.append(metadata)
                    if len(self.batch_ids) >= self.batch_size:
                        self.flush_batch()
        except Exception as e:
            self.dead_letter_queue.append(path)

    def flush_batch(self):
        if self.batch_ids:
            self.db.collection.upsert(
                ids=self.batch_ids,
                embeddings=self.batch_vectors,
                metadatas=self.batch_metadatas
            )
            self.batch_ids = []
            self.batch_vectors = []
            self.batch_metadatas = []

    def chunk_text(self, text, chunk_size=1000):
        # Simple chunking by characters, can be improved
        return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

    def retry_dead_letters(self):
        for path in self.dead_letter_queue[:]:
            try:
                self.handle_new_file(path)
                self.dead_letter_queue.remove(path)
            except Exception:
                continue
