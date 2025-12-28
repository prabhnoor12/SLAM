
import os
import platform
import subprocess
import webbrowser


def open_file(path, log=False):
    """
    Opens a file using the operating system's default application.
    This is cross-platform and non-blocking.
    """
    if not os.path.exists(path):
        if log:
            print(f"[!] Path does not exist: {path}")
        return False
    try:
        current_os = platform.system()
        if current_os == "Windows":
            os.startfile(path)
        elif current_os == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
        if log:
            print(f"[+] Opened file: {path}")
        return True
    except Exception as e:
        if log:
            print(f"[!] Launcher Error: {e}")
        return False

def open_folder(folder_path, log=False):
    """
    Opens a folder in the system's file explorer.
    """
    if not os.path.isdir(folder_path):
        if log:
            print(f"[!] Folder does not exist: {folder_path}")
        return False
    try:
        current_os = platform.system()
        if current_os == "Windows":
            os.startfile(folder_path)
        elif current_os == "Darwin":
            subprocess.Popen(["open", folder_path])
        else:
            subprocess.Popen(["xdg-open", folder_path])
        if log:
            print(f"[+] Opened folder: {folder_path}")
        return True
    except Exception as e:
        if log:
            print(f"[!] Folder Launcher Error: {e}")
        return False

def open_url(url, log=False):
    """
    Opens a URL in the default web browser.
    """
    try:
        webbrowser.open(url)
        if log:
            print(f"[+] Opened URL: {url}")
        return True
    except Exception as e:
        if log:
            print(f"[!] URL Launcher Error: {e}")
        return False