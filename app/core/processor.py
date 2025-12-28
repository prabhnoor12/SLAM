import os
import fitz
import pytesseract
import pathlib
from app.utils.diagnostics import logger, profile_performance
import concurrent.futures
import hashlib
import zipfile
import tarfile
from PIL import Image, ImageOps
from typing import Generator, Dict, List, Any, Optional

# Optional dependency for encoding detection
try:
    import chardet
except ImportError:
    chardet = None



# --- 🔌 Modern Extractor Architecture ---

class BaseExtractor:
    """Interface for all file extractors."""
    @staticmethod
    def extract_all(processor, path: str, options: dict) -> dict:
        raise NotImplementedError

    @staticmethod
    def yield_chunks(processor, path: str, max_length: int) -> Generator:
        raise NotImplementedError

class ProcessorRegistry:
    def __init__(self):
        self._registry: Dict[str, BaseExtractor] = {}

    def register(self, extensions: List[str]):
        def decorator(cls):
            for ext in extensions:
                self._registry[ext.lower()] = cls
            return cls
        return decorator

    def get(self, ext: str) -> Optional[BaseExtractor]:
        return self._registry.get(ext.lower())

registry = ProcessorRegistry()

# --- 📂 Implementation: PDF ---

@registry.register(['.pdf'])
class PDFExtractor(BaseExtractor):
    @staticmethod
    def extract_all(processor, path, options):
        result = {"text": [], "images": [], "metadata": {}}
        with fitz.open(path) as doc:
            result["metadata"] = doc.metadata
            for page in doc:
                blocks = page.get_text("blocks")
                for b in blocks:
                    if len(b[4].strip()) > 20:
                        result["text"].append({"text": b[4].strip(), "page": page.number + 1, "bbox": b[:4]})
        return result

    @staticmethod
    def yield_chunks(processor, path, max_length):
        with fitz.open(path) as doc:
            for page in doc:
                for b in page.get_text("blocks"):
                    if len(b[4].strip()) > 20:
                        yield {"text": b[4].strip(), "page": page.number + 1, "bbox": b[:4], "type": "pdf_block"}

# --- 🖼️ Implementation: Images ---

@registry.register(['.png', '.jpg', '.jpeg', '.tiff', '.bmp'])
class ImageExtractor(BaseExtractor):
    @staticmethod
    def extract_all(processor, path, options):
        return {"text": processor._extract_image_text(path), "images": [path], "metadata": {}}

    @staticmethod
    def yield_chunks(processor, path, max_length):
        text = processor._extract_image_text(path)
        if text.strip():
            yield {"text": text, "page": 1, "type": "ocr_result"}

# --- 📦 Implementation: Archives (ZIP) ---

@registry.register(['.zip'])
class ZipExtractor(BaseExtractor):
    MAX_SIZE = 100 * 1024 * 1024  # 100MB Safety Limit

    @staticmethod
    def extract_all(processor, path, options):
        result = {"text": [], "metadata": {"type": "archive"}}
        with zipfile.ZipFile(path, 'r') as z:
            for name in z.namelist():
                if z.getinfo(name).file_size > ZipExtractor.MAX_SIZE: continue
                if any(name.endswith(ext) for ext in ['.txt', '.md', '.py', '.log']):
                    with z.open(name) as f:
                        text = f.read().decode('utf-8', errors='replace')
                        result["text"].append({"text": text, "filename": name})
        return result

# --- 🚀 The Main Processor Engine ---

class FileProcessor:
    def __init__(self, ocr_lang='eng', max_workers=4):
        self.ocr_lang = ocr_lang
        self.tess_config = r'--oem 3 --psm 3'
        self.max_workers = max_workers

    @profile_performance
    def get_smart_chunks(self, path: str) -> Generator:
        ext = pathlib.Path(path).suffix.lower()
        extractor = registry.get(ext)
        if extractor:
            yield from extractor.yield_chunks(self, path, 1500)
        else:
            # Default text fallback
            text = self._extract_plain_text(path)
            if text: yield {"text": text, "page": 1, "type": "raw_text"}

    def _extract_image_text(self, path):
        with Image.open(path) as img:
            processed_img = ImageOps.grayscale(img)
            return pytesseract.image_to_string(processed_img, lang=self.ocr_lang, config=self.tess_config)

    @profile_performance
    def _extract_plain_text(self, path, max_length=10000):
        # Auto-encoding detection logic
        enc = 'utf-8'
        if chardet:
            with open(path, 'rb') as f:
                enc = chardet.detect(f.read(4096))['encoding'] or 'utf-8'
        
        try:
            with open(path, 'r', encoding=enc, errors='replace') as f:
                return f.read(max_length)
        except:
            return ""

    @profile_performance
    def batch_extract(self, paths: List[str]):
        """Hybrid Batch: Uses ProcessPool for CPU heavy tasks."""
        results = {}
        with concurrent.futures.ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_path = {executor.submit(self._extract_all_wrapper, p): p for p in paths}
            for future in concurrent.futures.as_completed(future_to_path):
                results[future_to_path[future]] = future.result()
        return results

    @staticmethod
    def _extract_all_wrapper(path):
        # Helper for pickling in ProcessPool
        p = FileProcessor()
        ext = pathlib.Path(path).suffix.lower()
        extractor = registry.get(ext)
        return extractor.extract_all(p, path, {}) if extractor else None