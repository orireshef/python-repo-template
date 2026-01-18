"""File handlers for different object types."""

from files_api.files.handlers.base import IFileHandler
from files_api.files.handlers.json_handler import JsonHandler
from files_api.files.handlers.numpy_handler import NumpyHandler

__all__ = [
    "IFileHandler",
    "JsonHandler",
    "NumpyHandler",
]
