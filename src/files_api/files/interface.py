"""Abstract base class for file systems."""

from abc import ABC, abstractmethod
from typing import IO, Any


class IFileSystem(ABC):
    """Abstract base class for file system implementations.

    Defines the interface for saving, retrieving, counting, and checking
    existence of objects in a storage backend. Concrete implementations
    provide storage-specific logic via the _open() method.
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

    @abstractmethod
    def _open(self, key: str, mode: str) -> IO[bytes]:
        """Open a file-like object for the given key.

        This is the abstract method that concrete implementations must provide.
        It returns a file-like object that handlers can write to or read from.

        Args:
            key: The full key including extension (e.g., "data.npy").
            mode: The file mode ("rb" for read, "wb" for write).

        Returns:
            A file-like object (IO[bytes]).

        Note:
            For LocalFileSystem, this opens a local file.
            For S3FileSystem, this would return an s3fs file object.
        """
        ...
