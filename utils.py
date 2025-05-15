# utils.py

import os
import logging

# Configure root logger
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s'
)

def read_text_file(path: str, encoding: str = 'utf-8') -> str:
    """Read and return text from the given file path."""
    with open(path, 'r', encoding=encoding) as f:
        return f.read()

def write_text_file(path: str, text: str, encoding: str = 'utf-8') -> None:
    """Write text to the given file path, creating directories as needed."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, 'w', encoding=encoding) as f:
        f.write(text)

def read_binary_file(path: str) -> bytes:
    """Read and return binary data from the given file path."""
    with open(path, 'rb') as f:
        return f.read()

def write_binary_file(path: str, data: bytes) -> None:
    """Write binary data to the given file path, creating directories as needed."""
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, 'wb') as f:
        f.write(data)

def ensure_dir(path: str) -> None:
    """Ensure that a directory exists at the given path."""
    os.makedirs(path, exist_ok=True)

def log_info(message: str) -> None:
    """Log an informational message."""
    logging.info(message)

def log_error(message: str) -> None:
    """Log an error message."""
    logging.error(message)
