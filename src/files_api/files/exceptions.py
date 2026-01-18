"""Custom exceptions for the files module."""

from typing import Any


class FilesError(Exception):
    """Base exception for files module."""

    pass


class SerializationError(FilesError):
    """Raised when an object cannot be serialized."""

    def __init__(self, obj: Any, reason: str):
        self.obj_type = type(obj).__name__
        self.reason = reason
        super().__init__(f"Cannot serialize object of type '{self.obj_type}': {reason}")


class DeserializationError(FilesError):
    """Raised when data cannot be deserialized."""

    def __init__(self, reason: str):
        self.reason = reason
        super().__init__(f"Cannot deserialize data: {reason}")


class FileNotFoundError(FilesError):
    """Raised when a key does not exist."""

    def __init__(self, key: str):
        self.key = key
        super().__init__(f"File not found for key: '{key}'")


class FileExistsError(FilesError):
    """Raised when trying to save to a key that already exists."""

    def __init__(self, key: str):
        self.key = key
        super().__init__(f"File already exists for key: '{key}'")
