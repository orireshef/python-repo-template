"""Handler for numpy arrays (.npy files)."""

import logging
from typing import IO, Any

import numpy as np

from files_api.files.exceptions import DeserializationError, SerializationError
from files_api.files.handlers.base import IFileHandler

logger = logging.getLogger(__name__)


class NumpyHandler(IFileHandler):
    """Handler for numpy arrays.

    Saves arrays as .npy files using numpy's native format.
    Works with any file-like object (local files, S3 via s3fs, etc.).
    """

    extension: str = ".npy"
    type_name: str = "numpy"

    def to_file(self, obj: Any, file_obj: IO[bytes]) -> None:
        """Write numpy array to a file-like object.

        Args:
            obj: A numpy ndarray.
            file_obj: A file-like object opened in binary write mode.

        Raises:
            SerializationError: If the array cannot be written.
        """
        logger.debug(
            "Writing numpy array (shape=%s, dtype=%s) to file",
            obj.shape,
            obj.dtype,
        )
        try:
            np.save(file_obj, obj, allow_pickle=True)
            logger.info("Wrote numpy array (shape=%s, dtype=%s)", obj.shape, obj.dtype)
        except Exception as e:  # pragma: no cover
            logger.error("Failed to write numpy array: %s", e)
            raise SerializationError(obj, str(e)) from e

    def from_file(self, file_obj: IO[bytes]) -> Any:
        """Read numpy array from a file-like object.

        Args:
            file_obj: A file-like object opened in binary read mode.

        Returns:
            The numpy array.

        Raises:
            DeserializationError: If the array cannot be read.
        """
        logger.debug("Reading numpy array from file")
        try:
            result = np.load(file_obj, allow_pickle=True)
            logger.info("Read numpy array (shape=%s, dtype=%s)", result.shape, result.dtype)
            return result
        except Exception as e:
            logger.error("Failed to read numpy array: %s", e)
            raise DeserializationError(str(e)) from e
