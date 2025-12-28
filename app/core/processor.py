import os
import shutil
import pathlib
import logging
import concurrent.futures
from pathlib import Path
from PIL import Image
import fitz  # PyMuPDF
import pytesseract

logger = logging.getLogger("SLAM_Processor")

class FileProcessor:
    def extract_text(self, path: str, max_length: int = 10000) -> str:
        """Central router for text extraction based on file signature."""
        path_obj = pathlib.Path(path)
        if not path_obj.exists():
            return ""
            
        ext = path_obj.suffix.lower()
        try:
            if ext == '.pdf':
                return self._extract_pdf_text(path, max_length)
            elif ext in {'.png', '.jpg', '.jpeg', '.tiff', '.bmp'}:
                return self._extract_image_text(path, max_length)
            # Default to plain text for everything else (txt, md, log, csv)
            return self._extract_plain_text(path, max_length)
        except Exception as e:
            logger.error(f"Failed to process {path}: {e}")
            return ""

    def _extract_pdf_text(self, path: str, max_length: int) -> str:
        text_parts = []
        with fitz.open(path) as doc:
            for page in doc:
                text_parts.append(page.get_text())
                if sum(len(p) for p in text_parts) > max_length:
                    break
        return "".join(text_parts)[:max_length]

    def _extract_image_text(self, path: str, max_length: int) -> str:
        # Crucial: Use with-statement to ensure file handle is released
        with Image.open(path) as img:
            text = pytesseract.image_to_string(img)
        return text[:max_length]

    def _extract_plain_text(self, path: str, max_length: int) -> str:
        # Use errors='replace' to prevent crashes on binary characters
        with open(path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read(max_length)

    def batch_extract_text(self, paths, max_length=10000, max_workers=4):
        """
        Uses ProcessPoolExecutor for CPU-bound OCR tasks.
        Threads are better for I/O, but Processes are better for OCR.
        """
        results = {}
        # We use ProcessPoolExecutor here because Tesseract is CPU-intensive
        with concurrent.futures.ProcessPoolExecutor(max_workers=max_workers) as executor:
            future_to_path = {
                executor.submit(self.extract_text, path, max_length): path 
                for path in paths
            }
            for future in concurrent.futures.as_completed(future_to_path):
                path = future_to_path[future]
                try:
                    results[path] = future.result()
                except Exception:
                    results[path] = ""
        return results

# --- 📂 Archive Function ---

def archive_on_index(file_path: str, archive_dir: str = "./archive") -> str:
    """
    Safely moves a file to an archive. Handles name collisions.
    """
    source = Path(file_path)
    if not source.exists():
        return file_path

    dest_dir = Path(archive_dir)
    dest_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate unique destination path
    destination = dest_dir / source.name
    counter = 1
    while destination.exists():
        destination = dest_dir / f"{source.stem}_{counter}{source.suffix}"
        counter += 1
    
    try:
        # shutil.move is safer than os.rename across different drives/partitions
        shutil.move(str(source), str(destination))
        return str(destination)
    except Exception as e:
        logger.error(f"Archive failed for {file_path}: {e}")
        return file_path