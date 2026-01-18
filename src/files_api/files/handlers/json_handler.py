"""Handler for JSON-serializable objects (.json files)."""

import json
import logging
from typing import IO, Any

from files_api.files.exceptions import DeserializationError, SerializationError
from files_api.files.handlers.base import IFileHandler

logger = logging.getLogger(__name__)

# Current envelope version
ENVELOPE_VERSION = 1


class JsonHandler(IFileHandler):
    """Handler for JSON-serializable objects.

    Saves objects as .json files with a metadata envelope containing
    type information for future extensibility.
    Works with any file-like object (local files, S3 via s3fs, etc.).
    """

    extension: str = ".json"
    type_name: str = "json"

    def to_file(self, obj: Any, file_obj: IO[bytes]) -> None:
        """Write object to a file-like object as JSON.

        Args:
            obj: A JSON-serializable object.
            file_obj: A file-like object opened in binary write mode.

        Raises:
            SerializationError: If the object cannot be serialized.
        """
        obj_type = type(obj).__name__
        logger.debug(
            "Writing JSON object (type=%s) with envelope version %d",
            obj_type,
            ENVELOPE_VERSION,
        )

        envelope = {
            "__type__": obj_type,
            "__version__": ENVELOPE_VERSION,
            "data": obj,
        }
        try:
            data = json.dumps(envelope, ensure_ascii=False).encode("utf-8")
            file_obj.write(data)
            logger.info("Wrote JSON object (type=%s, %d bytes)", obj_type, len(data))
        except TypeError as e:
            logger.error("Failed to serialize object of type %s: %s", obj_type, e)
            raise SerializationError(obj, str(e)) from e

    def from_file(self, file_obj: IO[bytes]) -> Any:
        """Read object from a file-like object as JSON.

        Args:
            file_obj: A file-like object opened in binary read mode.

        Returns:
            The deserialized object (the 'data' field from envelope).

        Raises:
            DeserializationError: If the data cannot be deserialized.
        """
        logger.debug("Reading JSON object from file")
        try:
            data = file_obj.read()
            envelope = json.loads(data.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            logger.error("Failed to parse JSON: %s", e)
            raise DeserializationError(str(e)) from e

        if not isinstance(envelope, dict) or "data" not in envelope:
            logger.error("Invalid envelope structure: missing 'data' field")
            raise DeserializationError("Invalid envelope: missing 'data' field")

        obj_type = envelope.get("__type__", "unknown")
        version = envelope.get("__version__", "unknown")
        logger.info("Read JSON object (type=%s, version=%s)", obj_type, version)
        return envelope["data"]
