"""Abstract base class for file handlers."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class IFileHandler(ABC):
    """Abstract base class for file type handlers.

    Each handler is responsible for serializing/deserializing a specific
    type of object to/from a specific file format.
    """

    extension: str  # e.g., ".npy", ".json"
    type_name: str  # stored in metadata for future extensibility

    @abstractmethod
    def serialize(self, obj: Any) -> bytes:
        """Convert object to bytes.

        Args:
            obj: The object to serialize.

        Returns:
            The serialized bytes.

        Raises:
            SerializationError: If the object cannot be serialized.
        """
        ...

    @abstractmethod
    def deserialize(self, data: bytes) -> Any:
        """Convert bytes to object.

        Args:
            data: The bytes to deserialize.

        Returns:
            The deserialized object.

        Raises:
            DeserializationError: If the data cannot be deserialized.
        """
        ...

    @abstractmethod
    def to_file(self, obj: Any, path: Path) -> None:
        """Write object directly to file path.

        Args:
            obj: The object to write.
            path: The file path to write to.

        Raises:
            SerializationError: If the object cannot be serialized.
        """
        ...

    @abstractmethod
    def from_file(self, path: Path) -> Any:
        """Read object directly from file path.

        Args:
            path: The file path to read from.

        Returns:
            The deserialized object.

        Raises:
            DeserializationError: If the file cannot be deserialized.
        """
        ...
