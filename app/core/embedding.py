
from sentence_transformers import SentenceTransformer
import numpy as np
import os


class EmbeddingEngine:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model_name = model_name
        self._model = None  # Lazy load

    @property
    def model(self):
        if self._model is None:
            self._model = SentenceTransformer(self.model_name)
        return self._model

    def encode(self, text):
        """
        Encode a single string or a list of strings.
        Uses batch encoding for lists for better performance.
        """
        if isinstance(text, list):
            return self.model.encode(text, normalize_embeddings=True)
        return self.model.encode([text], normalize_embeddings=True)[0]

    def save_embeddings(self, embeddings, file_path):
        """Save embeddings (numpy array) to disk."""
        np.save(file_path, embeddings)

    def load_embeddings(self, file_path):
        """Load embeddings (numpy array) from disk."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Embedding file not found: {file_path}")
        return np.load(file_path)

    def switch_model(self, model_name):
        """Switch to a different sentence transformer model at runtime."""
        if model_name != self.model_name:
            self.model_name = model_name
            self._model = SentenceTransformer(model_name)