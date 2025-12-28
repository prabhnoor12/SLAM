
import fitz
import pytesseract
import pathlib
from PIL import Image
import os

class FileProcessor:
    def extract_text(self, path, max_length=10000):
        """
        Extract text from PDF, image, or text file. Optionally limit text length.
        """
        ext = pathlib.Path(path).suffix.lower()
        try:
            if ext == '.pdf':
                with fitz.open(path) as doc:
                    text = "".join([page.get_text() for page in doc])
                return text[:max_length]
            elif ext in ['.png', '.jpg', '.jpeg']:
                with Image.open(path) as img:
                    return pytesseract.image_to_string(img)[:max_length]
            with open(path, 'r', errors='ignore') as f:
                return f.read(max_length)
        except Exception as e:
            return ""

    def extract_images_from_pdf(self, path, output_dir=None):
        """
        Extract images from a PDF and save to output_dir. Returns list of image file paths.
        """
        ext = pathlib.Path(path).suffix.lower()
        if ext != '.pdf':
            return []
        images = []
        with fitz.open(path) as doc:
            for i, page in enumerate(doc):
                for img_index, img in enumerate(page.get_images(full=True)):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    if output_dir is None:
                        output_dir = os.path.dirname(path)
                    os.makedirs(output_dir, exist_ok=True)
                    img_path = os.path.join(output_dir, f"page_{i+1}_img_{img_index+1}.{image_ext}")
                    with open(img_path, "wb") as img_file:
                        img_file.write(image_bytes)
                    images.append(img_path)
        return images

    def batch_extract_text(self, paths, max_length=10000):
        """
        Process multiple files and return a dict of {path: text}.
        """
        results = {}
        for path in paths:
            results[path] = self.extract_text(path, max_length=max_length)
        return results