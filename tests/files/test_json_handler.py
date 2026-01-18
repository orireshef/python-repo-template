"""Tests for JsonHandler."""

import json
import tempfile
from io import BytesIO
from pathlib import Path

import pytest

from files_api.files.exceptions import DeserializationError, SerializationError
from files_api.files.handlers.json_handler import JsonHandler


class TestJsonHandlerAttributes:
    """Test handler attributes."""

    def test_extension_is_json(self):
        handler = JsonHandler()
        assert handler.extension == ".json"

    def test_type_name_is_json(self):
        handler = JsonHandler()
        assert handler.type_name == "json"


class TestJsonHandlerToFile:
    """Test to_file method with file-like objects."""

    def test_to_file_dict(self):
        handler = JsonHandler()
        obj = {"key": "value", "number": 42}
        buffer = BytesIO()
        handler.to_file(obj, buffer)
        assert buffer.tell() > 0

    def test_to_file_list(self):
        handler = JsonHandler()
        obj = [1, 2, 3, "four"]
        buffer = BytesIO()
        handler.to_file(obj, buffer)
        assert buffer.tell() > 0

    def test_to_file_primitives(self):
        handler = JsonHandler()
        for obj in ["string", 42, 3.14, True, None]:
            buffer = BytesIO()
            handler.to_file(obj, buffer)
            assert buffer.tell() > 0

    def test_to_file_nested_structure(self):
        handler = JsonHandler()
        obj = {"nested": {"deep": [1, 2, {"key": "value"}]}}
        buffer = BytesIO()
        handler.to_file(obj, buffer)
        assert buffer.tell() > 0

    def test_to_file_unicode_strings(self):
        handler = JsonHandler()
        obj = {"emoji": "🎉", "chinese": "中文", "arabic": "العربية"}
        buffer = BytesIO()
        handler.to_file(obj, buffer)
        assert buffer.tell() > 0

    def test_to_file_includes_metadata_envelope(self):
        handler = JsonHandler()
        obj = {"data": "test"}
        buffer = BytesIO()
        handler.to_file(obj, buffer)
        buffer.seek(0)
        parsed = json.loads(buffer.read().decode("utf-8"))
        assert "__type__" in parsed
        assert "__version__" in parsed
        assert "data" in parsed

    def test_to_file_non_serializable_raises_error(self):
        handler = JsonHandler()

        class NotSerializable:
            pass

        buffer = BytesIO()
        with pytest.raises(SerializationError) as exc_info:
            handler.to_file(NotSerializable(), buffer)
        assert "NotSerializable" in str(exc_info.value)

    def test_to_file_error_includes_object_type(self):
        handler = JsonHandler()

        class MyCustomClass:
            pass

        buffer = BytesIO()
        with pytest.raises(SerializationError) as exc_info:
            handler.to_file(MyCustomClass(), buffer)
        assert exc_info.value.obj_type == "MyCustomClass"

    def test_to_file_with_real_file(self):
        handler = JsonHandler()
        obj = {"key": "value"}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            with open(path, "wb") as f:
                handler.to_file(obj, f)
            assert path.exists()
            assert path.stat().st_size > 0


class TestJsonHandlerFromFile:
    """Test from_file method with file-like objects."""

    def test_from_file_roundtrip_dict(self):
        handler = JsonHandler()
        obj = {"key": "value", "number": 42}
        buffer = BytesIO()
        handler.to_file(obj, buffer)
        buffer.seek(0)
        result = handler.from_file(buffer)
        assert result == obj

    def test_from_file_roundtrip_list(self):
        handler = JsonHandler()
        obj = [1, 2, 3, "four"]
        buffer = BytesIO()
        handler.to_file(obj, buffer)
        buffer.seek(0)
        result = handler.from_file(buffer)
        assert result == obj

    def test_from_file_roundtrip_nested(self):
        handler = JsonHandler()
        obj = {"nested": {"deep": [1, 2, {"key": "value"}]}}
        buffer = BytesIO()
        handler.to_file(obj, buffer)
        buffer.seek(0)
        result = handler.from_file(buffer)
        assert result == obj

    def test_from_file_invalid_json_raises_error(self):
        handler = JsonHandler()
        buffer = BytesIO(b"not valid json")
        with pytest.raises(DeserializationError):
            handler.from_file(buffer)

    def test_from_file_missing_envelope_raises_error(self):
        handler = JsonHandler()
        # Valid JSON but missing envelope
        data = json.dumps({"key": "value"}).encode("utf-8")
        buffer = BytesIO(data)
        with pytest.raises(DeserializationError):
            handler.from_file(buffer)

    def test_from_file_with_real_file(self):
        handler = JsonHandler()
        obj = {"test": "data"}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            with open(path, "wb") as f:
                handler.to_file(obj, f)
            with open(path, "rb") as f:
                result = handler.from_file(f)
            assert result == obj
