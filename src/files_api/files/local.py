"""Local filesystem implementation."""

import logging
from pathlib import Path
from typing import IO, Any

from files_api.files.exceptions import FileExistsError, FileNotFoundError
from files_api.files.factory import FileHandlerFactory
from files_api.files.interface import IFileSystem

logger = logging.getLogger(__name__)


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
        logger.info("Initialized LocalFileSystem at %s", self.base_path)

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
        logger.debug("save() called with key=%r, obj_type=%s", key, type(obj).__name__)

        # Check if any file with this key already exists
        existing = self._find_file(key)
        if existing is not None:
            logger.warning("Key %r already exists at %s", key, existing)
            raise FileExistsError(key)

        # Get the appropriate handler and build the full key with extension
        handler = self.factory.get_handler_for_object(obj)
        full_key = f"{key}{handler.extension}"
        logger.debug("Selected %s handler, full_key=%s", handler.type_name, full_key)

        # Save using handler with file-like object
        with self._open(full_key, "wb") as f:
            handler.to_file(obj, f)

        logger.info("Saved key=%r using %s handler", key, handler.type_name)

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
        logger.debug("get() called with key=%r", key)

        full_key = self._find_file(key)
        if full_key is None:
            logger.warning("Key %r not found in %s", key, self.base_path)
            raise FileNotFoundError(key)

        # Get handler based on file extension
        file_path = self.base_path / full_key
        handler = self.factory.get_handler_for_file(file_path)
        logger.debug("Found %s, using %s handler", full_key, handler.type_name)

        # Load using handler with file-like object
        with self._open(full_key, "rb") as f:
            result = handler.from_file(f)

        logger.info("Loaded key=%r using %s handler", key, handler.type_name)
        return result

    def count(self, prefix: str = "") -> int:
        """Count files matching prefix.

        Args:
            prefix: Optional prefix to filter files.

        Returns:
            The number of matching files.
        """
        pattern = f"{prefix}*" if prefix else "*"
        # Count files with known extensions
        total = 0
        for ext in [".json", ".npy"]:
            total += len(list(self.base_path.glob(f"{pattern}{ext}")))
        logger.debug("count(prefix=%r) = %d", prefix, total)
        return total

    def exists(self, key: str) -> bool:
        """Check if key exists.

        Args:
            key: The key to check (without extension).

        Returns:
            True if the key exists (with any extension), False otherwise.
        """
        found = self._find_file(key) is not None
        logger.debug("exists(key=%r) = %s", key, found)
        return found

    def _open(self, full_key: str, mode: str) -> IO[bytes]:
        """Open a local file for the given key.

        Args:
            full_key: The full key including extension (e.g., "data.npy").
            mode: The file mode ("rb" for read, "wb" for write).

        Returns:
            An open file object.
        """
        file_path = self.base_path / full_key
        logger.debug("Opening %s with mode=%r", file_path, mode)
        return open(file_path, mode)

    def _find_file(self, key: str) -> str | None:
        """Find a file by key (checking all known extensions).

        Args:
            key: The key to find (without extension).

        Returns:
            The full key with extension if found, None otherwise.
        """
        for ext in [".json", ".npy"]:
            full_key = f"{key}{ext}"
            path = self.base_path / full_key
            if path.exists():
                return full_key
        return None
