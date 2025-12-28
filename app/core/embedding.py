
from sentence_transformers import SentenceTransformer
import numpy as np
import os
import importlib
from typing import Any, Dict

class EmbeddingModel:
    """
    Base class for embedding models.
    """
    def embed(self, text: str) -> Any:
        raise NotImplementedError("embed() must be implemented by subclasses.")


class TransformerEmbeddingModel(EmbeddingModel):
    def __init__(self, model_name: str = "sentence-transformers/all-MiniLM-L6-v2"):
        try:
            self.model = importlib.import_module("sentence_transformers").SentenceTransformer(model_name)
        except Exception as e:
            raise ImportError(f"Could not import transformer model: {e}")

    def embed(self, text: str) -> Any:
        return self.model.encode(text)


class MultilingualEmbeddingModel(EmbeddingModel):
    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        try:
            self.model = importlib.import_module("sentence_transformers").SentenceTransformer(model_name)
        except Exception as e:
            raise ImportError(f"Could not import multilingual model: {e}")

    def embed(self, text: str) -> Any:
        return self.model.encode(text)


class DomainSpecificEmbeddingModel(EmbeddingModel):
    def __init__(self, model_name: str):
        try:
            self.model = importlib.import_module("sentence_transformers").SentenceTransformer(model_name)
        except Exception as e:
            raise ImportError(f"Could not import domain-specific model: {e}")

    def embed(self, text: str) -> Any:
        return self.model.encode(text)


class EmbeddingModelFactory:
    """
    Factory for creating embedding models based on configuration.
    """
    @staticmethod
    def get_model(model_type: str, model_name: str = None) -> EmbeddingModel:
        if model_type == "transformer":
            return TransformerEmbeddingModel(model_name or "sentence-transformers/all-MiniLM-L6-v2")
        elif model_type == "multilingual":
            return MultilingualEmbeddingModel(model_name or "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
        elif model_type == "domain-specific":
            if not model_name:
                raise ValueError("Domain-specific model requires a model_name.")
            return DomainSpecificEmbeddingModel(model_name)
        else:
            raise ValueError(f"Unknown model type: {model_type}")


def get_embedding(text: str, config: Dict[str, Any]) -> Any:
    """
    Get embedding for text using selected model from config.
    config example: {"type": "transformer", "model_name": "sentence-transformers/all-MiniLM-L6-v2"}
    """
    model_type = config.get("type", "transformer")
    model_name = config.get("model_name")
    model = EmbeddingModelFactory.get_model(model_type, model_name)
    return model.embed(text)


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