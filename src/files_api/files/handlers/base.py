"""Abstract base class for file handlers."""

from abc import ABC, abstractmethod
from typing import IO, Any


class IFileHandler(ABC):
    """Abstract base class for file type handlers.

    Each handler is responsible for writing/reading a specific type of object
    to/from a file-like object. The file-like object can be a local file,
    an S3 file (via s3fs), or any other IO[bytes] compatible object.
    """

    extension: str  # e.g., ".npy", ".json"
    type_name: str  # handler identifier for logging

    @abstractmethod
    def to_file(self, obj: Any, file_obj: IO[bytes]) -> None:
        """Write object to a file-like object.

        Args:
            obj: The object to write.
            file_obj: A file-like object opened in binary write mode.

        Raises:
            SerializationError: If the object cannot be written.
        """
        ...

    @abstractmethod
    def from_file(self, file_obj: IO[bytes]) -> Any:
        """Read object from a file-like object.

        Args:
            file_obj: A file-like object opened in binary read mode.

        Returns:
            The deserialized object.

        Raises:
            DeserializationError: If the object cannot be read.
        """
        ...
