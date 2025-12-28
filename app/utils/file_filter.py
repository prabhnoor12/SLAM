import os
import mimetypes

# Patterns and extensions to exclude
EXCLUDE_DIRS = {
    '.git', '__pycache__', 'node_modules', 'venv', 'env', '.mypy_cache', '.pytest_cache', '.idea', '.vscode',
}
EXCLUDE_FILENAMES = {
    '.DS_Store', 'package-lock.json', 'yarn.lock', 'Pipfile.lock', 'poetry.lock',
}
EXCLUDE_EXTENSIONS = {
    # Binaries and compiled
    '.exe', '.dll', '.so', '.bin', '.class', '.pyc', '.pyo', '.o', '.a', '.lib', '.obj',
    # Media
    '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.ico', '.svg', '.mp3', '.mp4', '.avi', '.mov', '.wav',
    # Archives
    '.zip', '.tar', '.gz', '.rar', '.7z', '.bz2', '.xz',
    # Documents
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.rtf', '.odt', '.ods', '.odp',
    # Misc
    '.db', '.sqlite', '.log', '.tmp', '.swp', '.bak',
}

def is_text_file(filepath, blocksize=1024):
    """
    Heuristically check if a file is a text file.
    Returns True for text files, False for binaries.
    """
    try:
        with open(filepath, 'rb') as f:
            chunk = f.read(blocksize)
            if b'\0' in chunk:
                return False
        # Optionally use mimetypes for further filtering
        mime, _ = mimetypes.guess_type(filepath)
        if mime and not mime.startswith('text'):
            return False
        return True
    except Exception:
        return False

def should_exclude(path):
    """
    Return True if the file or directory should be excluded from semantic search.
    """
    name = os.path.basename(path)
    # Exclude by directory name
    if name in EXCLUDE_DIRS:
        return True
    # Exclude by filename
    if name in EXCLUDE_FILENAMES:
        return True
    # Exclude by extension
    _, ext = os.path.splitext(name)
    if ext.lower() in EXCLUDE_EXTENSIONS:
        return True
    return False

def filter_files(file_list):
    """
    Filter out files and directories that should be excluded from semantic search.
    Only returns text files that are not in excluded patterns.
    """
    filtered = []
    for f in file_list:
        if should_exclude(f):
            continue
        if os.path.isdir(f):
            continue
        if not is_text_file(f):
            continue
        filtered.append(f)
    return filtered