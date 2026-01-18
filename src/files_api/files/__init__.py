"""Intelligent file storage API with automatic format selection."""

from files_api.files.exceptions import (
    DeserializationError,
    FileExistsError,
    FileNotFoundError,
    FilesError,
    SerializationError,
)
from files_api.files.interface import IFileSystem
from files_api.files.local import LocalFileSystem

__all__ = [
    "DeserializationError",
    "FileExistsError",
    "FileNotFoundError",
    "FilesError",
    "IFileSystem",
    "LocalFileSystem",
    "SerializationError",
]
