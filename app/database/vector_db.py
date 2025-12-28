import chromadb
from threading import Lock

class VectorStore:
    _instance = None
    _lock = Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(VectorStore, cls).__new__(cls)
                cls._instance.client = chromadb.PersistentClient(path="./slam_db")
                cls._instance.collection = cls._instance.client.get_or_create_collection(
                    name="local_files", metadata={"hnsw:space": "cosine"}
                )
            return cls._instance

    def query(self, query_vector, n=10):
        results = self.collection.query(query_embeddings=[query_vector.tolist()], n_results=n)
        output = []
        if not results['ids'][0]: return []
        for i in range(len(results['ids'][0])):
            dist = results['distances'][0][i]
            output.append({
                "metadata": results['metadatas'][0][i],
                "score": round(max(0, 100 - (dist * 100)), 1)
            })
        return output