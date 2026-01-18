"""Handler for JSON-serializable objects (.json files)."""

import json
from pathlib import Path
from typing import Any

from files_api.files.exceptions import DeserializationError, SerializationError
from files_api.files.handlers.base import IFileHandler

# Current envelope version
ENVELOPE_VERSION = 1


class JsonHandler(IFileHandler):
    """Handler for JSON-serializable objects.

    Saves objects as .json files with a metadata envelope containing
    type information for future extensibility.
    """

    extension: str = ".json"
    type_name: str = "json"

    def serialize(self, obj: Any) -> bytes:
        """Convert object to bytes with metadata envelope.

        Args:
            obj: A JSON-serializable object.

        Returns:
            The serialized bytes in JSON format with envelope.

        Raises:
            SerializationError: If the object cannot be serialized.
        """
        envelope = {
            "__type__": type(obj).__name__,
            "__version__": ENVELOPE_VERSION,
            "data": obj,
        }
        try:
            return json.dumps(envelope, ensure_ascii=False).encode("utf-8")
        except TypeError as e:
            raise SerializationError(obj, str(e)) from e

    def deserialize(self, data: bytes) -> Any:
        """Convert bytes to object, unwrapping metadata envelope.

        Args:
            data: The bytes in JSON format with envelope.

        Returns:
            The deserialized object (the 'data' field from envelope).

        Raises:
            DeserializationError: If the data cannot be deserialized.
        """
        try:
            envelope = json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise DeserializationError(str(e)) from e

        if not isinstance(envelope, dict) or "data" not in envelope:
            raise DeserializationError("Invalid envelope: missing 'data' field")

        return envelope["data"]

    def to_file(self, obj: Any, path: Path) -> None:
        """Write object directly to file.

        Args:
            obj: A JSON-serializable object.
            path: The file path to write to.

        Raises:
            SerializationError: If the object cannot be serialized.
        """
        data = self.serialize(obj)
        path.write_bytes(data)

    def from_file(self, path: Path) -> Any:
        """Read object directly from file.

        Args:
            path: The file path to read from.

        Returns:
            The deserialized object.

        Raises:
            DeserializationError: If the file cannot be deserialized.
        """
        try:
            data = path.read_bytes()
        except OSError as e:
            raise DeserializationError(str(e)) from e

        return self.deserialize(data)
