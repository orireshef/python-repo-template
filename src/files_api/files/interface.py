"""Abstract base class for file systems."""

from abc import ABC, abstractmethod
from typing import Any


class IFileSystem(ABC):
    """Abstract base class for file system implementations.

    Defines the interface for saving, retrieving, counting, and checking
    existence of objects in a storage backend.
    """

    @abstractmethod
    def save(self, key: str, obj: Any) -> None:
        """Save object with given key.

        Args:
            key: The key to save the object under (without extension).
            obj: The object to save.

        Raises:
            FileExistsError: If a file with this key already exists.
            SerializationError: If the object cannot be serialized.
        """
        ...

    @abstractmethod
    def get(self, key: str) -> Any:
        """Get object by key.

        Args:
            key: The key to retrieve (without extension).

        Returns:
            The deserialized object.

        Raises:
            FileNotFoundError: If the key does not exist.
            DeserializationError: If the file cannot be deserialized.
        """
        ...

    @abstractmethod
    def count(self, prefix: str = "") -> int:
        """Count files matching prefix.

        Args:
            prefix: Optional prefix to filter files.

        Returns:
            The number of matching files.
        """
        ...

    @abstractmethod
    def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: The key to check (without extension).

        Returns:
            True if the key exists, False otherwise.
        """
        ...
