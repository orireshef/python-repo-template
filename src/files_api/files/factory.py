"""Factory for selecting appropriate file handlers."""

from pathlib import Path
from typing import Any

import numpy as np

from files_api.files.handlers.base import IFileHandler
from files_api.files.handlers.json_handler import JsonHandler
from files_api.files.handlers.numpy_handler import NumpyHandler


class FileHandlerFactory:
    """Factory for selecting the appropriate file handler.

    Selects handlers based on object type (for saving) or file extension
    (for loading). Only numpy ndarrays use NumpyHandler, everything else
    falls back to JsonHandler.
    """

    def __init__(self):
        """Initialize the factory with default handlers."""
        self._numpy_handler = NumpyHandler()
        self._json_handler = JsonHandler()
        self._extension_map: dict[str, IFileHandler] = {
            ".npy": self._numpy_handler,
            ".json": self._json_handler,
        }

    def get_handler_for_object(self, obj: Any) -> IFileHandler:
        """Select handler based on object type.

        Priority:
        1. np.ndarray → NumpyHandler
        2. Everything else → JsonHandler (fallback)

        Args:
            obj: The object to find a handler for.

        Returns:
            The appropriate handler for the object type.
        """
        # Only numpy ndarrays use NumpyHandler
        if isinstance(obj, np.ndarray):
            return self._numpy_handler

        # Fallback to JSON for everything else
        return self._json_handler

    def get_handler_for_file(self, path: Path) -> IFileHandler:
        """Select handler based on file extension.

        Args:
            path: The file path to find a handler for.

        Returns:
            The appropriate handler for the file extension.

        Raises:
            ValueError: If the extension is not recognized.
        """
        suffix = path.suffix.lower()
        if suffix not in self._extension_map:
            raise ValueError(f"Unknown file extension: '{suffix}'")
        return self._extension_map[suffix]
