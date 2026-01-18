"""Handler for numpy objects (.npy files)."""

from io import BytesIO
from pathlib import Path
from typing import Any

import numpy as np

from files_api.files.exceptions import DeserializationError, SerializationError
from files_api.files.handlers.base import IFileHandler


class NumpyHandler(IFileHandler):
    """Handler for numpy arrays and objects with dtype attribute.

    Saves objects as .npy files using numpy's native format.
    """

    extension: str = ".npy"
    type_name: str = "numpy"

    def serialize(self, obj: Any) -> bytes:
        """Convert numpy object to bytes.

        Args:
            obj: A numpy array or object with dtype attribute.

        Returns:
            The serialized bytes in .npy format.

        Raises:
            SerializationError: If the object cannot be serialized.
        """
        try:
            buffer = BytesIO()
            np.save(buffer, obj, allow_pickle=False)
            return buffer.getvalue()
        except Exception as e:
            raise SerializationError(obj, str(e)) from e

    def deserialize(self, data: bytes) -> Any:
        """Convert bytes to numpy object.

        Args:
            data: The bytes in .npy format.

        Returns:
            The deserialized numpy object.

        Raises:
            DeserializationError: If the data cannot be deserialized.
        """
        try:
            buffer = BytesIO(data)
            return np.load(buffer, allow_pickle=False)
        except Exception as e:
            raise DeserializationError(str(e)) from e

    def to_file(self, obj: Any, path: Path) -> None:
        """Write numpy object directly to file.

        Args:
            obj: A numpy array or object with dtype attribute.
            path: The file path to write to.

        Raises:
            SerializationError: If the object cannot be serialized.
        """
        try:
            np.save(path, obj, allow_pickle=False)
        except Exception as e:
            raise SerializationError(obj, str(e)) from e

    def from_file(self, path: Path) -> Any:
        """Read numpy object directly from file.

        Args:
            path: The file path to read from.

        Returns:
            The deserialized numpy object.

        Raises:
            DeserializationError: If the file cannot be deserialized.
        """
        try:
            return np.load(path, allow_pickle=False)
        except Exception as e:
            raise DeserializationError(str(e)) from e
