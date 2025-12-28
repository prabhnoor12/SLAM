# SLAM
Smart Local Assets Manager
# SLAM: Smart Local Assets Manager 🚀

SLAM is a high-performance desktop application built in Python that uses local AI to provide **Semantic Search** across your local files. Unlike traditional search, SLAM understands the *meaning* of your documents, allowing you to find files based on concepts rather than just filenames.

## ✨ Features
- **Semantic Search:** Find files using natural language (e.g., "tax documents from last year").
- **Local AI:** All processing stays on your machine. No data ever leaves your computer.
- **Auto-Indexing:** Background "Watcher" service detects new files and indexes them instantly.
- **Cross-Platform:** Works on Windows, macOS, and Linux.
- **OCR Support:** Can "read" text inside images and scanned PDFs.

## 🛠️ Prerequisites
- **Python 3.9+**
- **Tesseract OCR:** Required for reading text from images.
  - *Windows:* [Download Installer](https://github.com/UB-Mannheim/tesseract/wiki)
  - *macOS:* `brew install tesseract`
  - *Linux:* `sudo apt install tesseract-ocr`

## 🚀 Getting Started

### 1. Clone & Setup
```bash
git clone [https://github.com/your-username/slam.git](https://github.com/your-username/slam.git)
cd slam