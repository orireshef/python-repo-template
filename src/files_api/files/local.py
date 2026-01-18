"""Local filesystem implementation."""

from pathlib import Path
from typing import Any

from files_api.files.exceptions import FileExistsError, FileNotFoundError
from files_api.files.factory import FileHandlerFactory
from files_api.files.interface import IFileSystem


class LocalFileSystem(IFileSystem):
    """Local filesystem implementation.

    Stores files on the local disk with automatic format selection
    based on object type.
    """

    def __init__(self, base_path: str | Path):
        """Initialize the local filesystem.

        Args:
            base_path: The base directory for file storage.
                       Will be created if it doesn't exist.
        """
        self.base_path = Path(base_path)
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.factory = FileHandlerFactory()

    def save(self, key: str, obj: Any) -> None:
        """Save object with given key.

        The file extension is determined automatically based on the object type.
        Raises FileExistsError if a file with this key already exists
        (with any extension).

        Args:
            key: The key to save the object under (without extension).
            obj: The object to save.

        Raises:
            FileExistsError: If a file with this key already exists.
            SerializationError: If the object cannot be serialized.
        """
        # Check if any file with this key already exists
        if self._find_file(key) is not None:
            raise FileExistsError(key)

        # Get the appropriate handler and build the path
        handler = self.factory.get_handler_for_object(obj)
        file_path = self.base_path / f"{key}{handler.extension}"

        # Save the file
        handler.to_file(obj, file_path)

    def get(self, key: str) -> Any:
        """Get object by key.

        The file extension is detected automatically from existing files.

        Args:
            key: The key to retrieve (without extension).

        Returns:
            The deserialized object.

        Raises:
            FileNotFoundError: If the key does not exist.
            DeserializationError: If the file cannot be deserialized.
        """
        file_path = self._find_file(key)
        if file_path is None:
            raise FileNotFoundError(key)

        handler = self.factory.get_handler_for_file(file_path)
        return handler.from_file(file_path)

    def count(self, prefix: str = "") -> int:
        """Count files matching prefix.

        Args:
            prefix: Optional prefix to filter files.

        Returns:
            The number of matching files.
        """
        pattern = f"{prefix}*" if prefix else "*"
        # Count files with known extensions
        count = 0
        for ext in [".json", ".npy"]:
            count += len(list(self.base_path.glob(f"{pattern}{ext}")))
        return count

    def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: The key to check (without extension).

        Returns:
            True if the key exists (with any extension), False otherwise.
        """
        return self._find_file(key) is not None

    def _find_file(self, key: str) -> Path | None:
        """Find a file by key (checking all known extensions).

        Args:
            key: The key to find (without extension).

        Returns:
            The path to the file if found, None otherwise.
        """
        for ext in [".json", ".npy"]:
            path = self.base_path / f"{key}{ext}"
            if path.exists():
                return path
        return None
