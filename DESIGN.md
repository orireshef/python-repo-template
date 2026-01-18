# System Design

## System Goal

Build an intelligent file storage API that:
- Automatically selects optimal file format based on object type
- Abstracts storage backend (local filesystem now, S3-compatible later)
- Provides consistent interface: `save`, `get`, `count`, `exists`
- Pure logic layer (no HTTP/FastAPI, just classes and functions)
- Prevents file collisions (same key already exists)

## KPIs

- 100% test coverage for serialization/deserialization
- Type detection accuracy: correctly identify numpy vs JSON-serializable objects
- Extensibility: adding new file types requires only implementing `IFileHandler`
- File collision detection: prevent overwriting existing files

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        IFileSystem                          │
│         (Abstract: save, get, count, exists)                │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      LocalFileSystem                        │
│  - base_path: Path                                          │
│  - factory: FileHandlerFactory                              │
│  - save/get/count/exists implementations                    │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    FileHandlerFactory                       │
│  - get_handler_for_object(obj) → IFileHandler               │
│  - get_handler_for_file(path) → IFileHandler                │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────┐
│      NumpyHandler       │     │      JsonHandler        │
│  extension: .npy        │     │  extension: .json       │
│  dtype objects          │     │  fallback (JSON-able)   │
└─────────────────────────┘     └─────────────────────────┘
```

## Components

### IFileSystem (Abstract Base Class)
- `save(key, obj)` - Save object, raises FileExistsError if key exists
- `get(key)` - Get object, raises FileNotFoundError if missing
- `count(prefix)` - Count files matching prefix
- `exists(key)` - Check if key exists

### IFileHandler (Abstract Base Class)
- `extension` - File extension (e.g., ".npy", ".json")
- `type_name` - Type identifier for metadata
- `serialize(obj)` - Convert object to bytes
- `deserialize(data)` - Convert bytes to object
- `to_file(obj, path)` - Write directly to file
- `from_file(path)` - Read directly from file

### NumpyHandler
- Handles objects with `dtype` attribute (ndarray, scalars)
- Uses numpy.save/numpy.load

### JsonHandler
- Fallback for JSON-serializable objects
- Wraps data in metadata envelope with `__type__` and `__version__`
- Raises SerializationError for non-serializable objects

### FileHandlerFactory
- Priority: numpy (dtype check) → JSON (fallback)
- Maps file extensions to handlers

### Custom Exceptions
- `FilesError` - Base exception
- `SerializationError` - Object cannot be serialized
- `DeserializationError` - Data cannot be deserialized
- `FileNotFoundError` - Key does not exist
- `FileExistsError` - Key already exists (collision)
