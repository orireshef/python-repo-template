# Files API

An intelligent file storage API for Python that automatically selects the optimal file format based on object type.

## Features

- **Automatic format selection** — numpy arrays → `.npy`, everything else → `.json`
- **Simple interface** — `save`, `get`, `exists`, `count`
- **File collision prevention** — raises error if key already exists
- **Extensible** — add new handlers or storage backends easily
- **S3-ready architecture** — designed for future s3fs integration
- **Comprehensive logging** — debug production issues easily

## Installation

```bash
# Clone the repository
git clone https://github.com/orireshef/python-repo-template.git
cd python-repo-template

# Install with uv
uv sync
```

## Quick Start

```python
from files_api.files import LocalFileSystem
import numpy as np

# Initialize storage
fs = LocalFileSystem("./data")

# Save a numpy array → automatically saved as .npy
matrix = np.array([[1, 2, 3], [4, 5, 6]])
fs.save("my_matrix", matrix)

# Save a dictionary → automatically saved as .json
config = {"name": "project", "version": "1.0"}
fs.save("config", config)

# Retrieve objects
loaded_matrix = fs.get("my_matrix")  # Returns numpy array
loaded_config = fs.get("config")      # Returns dict

# Check existence and count
fs.exists("my_matrix")  # True
fs.count()              # 2
fs.count("my_")         # 1 (prefix filter)
```

## API Reference

### LocalFileSystem

```python
from files_api.files import LocalFileSystem

fs = LocalFileSystem(base_path)
```

| Method | Description |
|--------|-------------|
| `save(key, obj)` | Save object with automatic format selection. Raises `FileExistsError` if key exists. |
| `get(key)` | Retrieve object by key. Raises `FileNotFoundError` if missing. |
| `exists(key)` | Check if key exists (returns bool). |
| `count(prefix="")` | Count files, optionally filtered by prefix. |

### Supported Types

| Object Type | File Format | Handler |
|-------------|-------------|---------|
| `np.ndarray` | `.npy` | NumpyHandler |
| `dict`, `list`, `str`, `int`, etc. | `.json` | JsonHandler |

### Exceptions

```python
from files_api.files import (
    FilesError,           # Base exception
    SerializationError,   # Object cannot be serialized
    DeserializationError, # File cannot be read
    FileNotFoundError,    # Key doesn't exist
    FileExistsError,      # Key already exists
)
```

## Examples

See [`scripts/usage_example.py`](scripts/usage_example.py) for a complete demonstration:

```bash
uv run python scripts/usage_example.py
```

This shows:
1. Saving and loading numpy arrays
2. Saving and loading dictionaries/lists
3. Checking existence and counting files
4. Object arrays (numpy arrays containing Python objects)

## Logging

The API uses Python's standard logging. Enable debug logs to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Now you'll see:
# DEBUG:files_api.files.local:save() called with key='matrix', obj_type=ndarray
# DEBUG:files_api.files.factory:Selected NumpyHandler for ndarray (shape=(2, 3), dtype=float64)
# INFO:files_api.files.handlers.numpy_handler:Wrote numpy array (shape=(2, 3), dtype=float64)
# INFO:files_api.files.local:Saved key='matrix' using numpy handler
```

## Architecture

```
IFileSystem (abstract)
    └── LocalFileSystem
    └── S3FileSystem (future)

IFileHandler (abstract)  
    └── NumpyHandler (.npy)
    └── JsonHandler (.json)

FileHandlerFactory
    └── get_handler_for_object(obj) → IFileHandler
    └── get_handler_for_file(path) → IFileHandler
```

### Extending for S3

The architecture uses file-like objects (`IO[bytes]`) so handlers work with any storage backend:

```python
import s3fs

class S3FileSystem(IFileSystem):
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.s3 = s3fs.S3FileSystem()
    
    def _open(self, key: str, mode: str):
        return self.s3.open(f"s3://{self.bucket}/{key}", mode)
```

See [`DESIGN.md`](DESIGN.md) for full architecture details.

## Development

```bash
# Run tests
uv run pytest

# Run tests with coverage
uv run pytest --cov=src/files_api --cov-report=term-missing

# Lint and format
uv run ruff check .
uv run ruff format .
```

## Project Structure

```
src/files_api/
├── __init__.py
└── files/
    ├── __init__.py          # Public exports
    ├── interface.py          # IFileSystem abstract base
    ├── local.py              # LocalFileSystem implementation
    ├── factory.py            # FileHandlerFactory
    ├── exceptions.py         # Custom exceptions
    └── handlers/
        ├── __init__.py
        ├── base.py           # IFileHandler abstract base
        ├── numpy_handler.py  # .npy file handler
        └── json_handler.py   # .json file handler

tests/files/                  # Test suite (77 tests, 100% coverage)
scripts/usage_example.py      # Usage demonstration
```

## License

MIT
