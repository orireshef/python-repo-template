# System Design

## System Goal

Build an intelligent file storage API that:
- Automatically selects optimal file format based on object type
- Abstracts storage backend (local filesystem now, S3 via s3fs later)
- Provides consistent interface: `save`, `get`, `count`, `exists`
- Pure logic layer (no HTTP/FastAPI, just classes and functions)
- Prevents file collisions (same key already exists)
- Comprehensive logging for production debugging

## KPIs

- 100% test coverage
- Type detection accuracy: correctly identify numpy ndarrays vs JSON-serializable objects
- Extensibility: adding new file types requires only implementing `IFileHandler`
- Storage backend extensibility: adding new backends (S3) requires only implementing `_open()`
- File collision detection: prevent overwriting existing files

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        IFileSystem                          │
│  Abstract: save, get, count, exists, _open                  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│    LocalFileSystem      │     │    S3FileSystem         │
│  _open() → local file   │     │  _open() → s3fs file    │
│                         │     │  (future)               │
└─────────────────────────┘     └─────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FileHandlerFactory                       │
│  - get_handler_for_object(obj) → IFileHandler               │
│  - get_handler_for_file(path) → IFileHandler                │
└─────────────────────────────────────────────────────────────┘
              │
              ▼
┌─────────────────────────────────────────────────────────────┐
│                       IFileHandler                          │
│  Abstract: to_file(obj, IO[bytes]), from_file(IO[bytes])    │
└─────────────────────────────────────────────────────────────┘
              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│      NumpyHandler       │     │      JsonHandler        │
│  extension: .npy        │     │  extension: .json       │
│  np.ndarray only        │     │  fallback (JSON-able)   │
└─────────────────────────┘     └─────────────────────────┘
```

## Key Design Decisions

### File-like Object Abstraction

Handlers work with `IO[bytes]` (file-like objects) instead of file paths. This enables:
- **Local files**: `open(path, "rb"/"wb")`
- **S3 files**: `s3fs.S3FileSystem().open("s3://bucket/key", "rb"/"wb")`
- **In-memory**: `BytesIO()` for testing

The `_open(key, mode)` abstract method is implemented by each FileSystem to provide
the appropriate file-like object for its storage backend.

### Handler Selection

- `np.ndarray` → NumpyHandler (.npy)
- Everything else → JsonHandler (.json)

Numpy scalars (np.float64, etc.) are NOT ndarrays and go to JsonHandler.

### allow_pickle=True for Numpy

Enabled to support object arrays (arrays containing Python objects like dicts).
The file format is still .npy - pickle is used internally for object serialization.

## Components

### IFileSystem (Abstract Base Class)
- `save(key, obj)` - Save object, raises FileExistsError if key exists
- `get(key)` - Get object, raises FileNotFoundError if missing
- `count(prefix)` - Count files matching prefix
- `exists(key)` - Check if key exists
- `_open(key, mode)` - Abstract: returns IO[bytes] for the storage backend

### IFileHandler (Abstract Base Class)
- `extension` - File extension (e.g., ".npy", ".json")
- `type_name` - Type identifier for logging
- `to_file(obj, file_obj)` - Write object to file-like object
- `from_file(file_obj)` - Read object from file-like object

### NumpyHandler
- Handles `np.ndarray` objects only
- Uses `np.save(file_obj, ...)` / `np.load(file_obj, ...)`
- Supports object arrays via `allow_pickle=True`

### JsonHandler
- Fallback for JSON-serializable objects
- Wraps data in metadata envelope with `__type__` and `__version__`
- Raises SerializationError for non-serializable objects

### FileHandlerFactory
- `get_handler_for_object(obj)`: isinstance(obj, np.ndarray) → Numpy, else JSON
- `get_handler_for_file(path)`: extension mapping

### Custom Exceptions
- `FilesError` - Base exception
- `SerializationError` - Object cannot be serialized (includes obj_type)
- `DeserializationError` - Data cannot be deserialized
- `FileNotFoundError` - Key does not exist
- `FileExistsError` - Key already exists (collision)

## Future: S3FileSystem

To add S3 support:

```python
import s3fs

class S3FileSystem(IFileSystem):
    def __init__(self, bucket: str):
        self.bucket = bucket
        self.fs = s3fs.S3FileSystem()
        self.factory = FileHandlerFactory()
    
    def _open(self, key: str, mode: str) -> IO[bytes]:
        return self.fs.open(f"s3://{self.bucket}/{key}", mode)
    
    # save/get/count/exists reuse the same logic as LocalFileSystem
```

The handlers work unchanged because they only interact with file-like objects.
