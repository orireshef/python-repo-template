"""Tests for JsonHandler."""

import json
import tempfile
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


class TestJsonHandlerSerialize:
    """Test serialize method."""

    def test_serialize_dict(self):
        handler = JsonHandler()
        obj = {"key": "value", "number": 42}
        result = handler.serialize(obj)
        assert isinstance(result, bytes)

    def test_serialize_list(self):
        handler = JsonHandler()
        obj = [1, 2, 3, "four"]
        result = handler.serialize(obj)
        assert isinstance(result, bytes)

    def test_serialize_primitives(self):
        handler = JsonHandler()
        for obj in ["string", 42, 3.14, True, None]:
            result = handler.serialize(obj)
            assert isinstance(result, bytes)

    def test_serialize_nested_structure(self):
        handler = JsonHandler()
        obj = {"nested": {"deep": [1, 2, {"key": "value"}]}}
        result = handler.serialize(obj)
        assert isinstance(result, bytes)

    def test_serialize_unicode_strings(self):
        handler = JsonHandler()
        obj = {"emoji": "🎉", "chinese": "中文", "arabic": "العربية"}
        result = handler.serialize(obj)
        assert isinstance(result, bytes)

    def test_serialize_includes_metadata_envelope(self):
        handler = JsonHandler()
        obj = {"data": "test"}
        result = handler.serialize(obj)
        parsed = json.loads(result.decode("utf-8"))
        assert "__type__" in parsed
        assert "__version__" in parsed
        assert "data" in parsed

    def test_serialize_non_serializable_raises_error(self):
        handler = JsonHandler()

        class NotSerializable:
            pass

        with pytest.raises(SerializationError) as exc_info:
            handler.serialize(NotSerializable())
        assert "NotSerializable" in str(exc_info.value)

    def test_serialization_error_includes_object_type(self):
        handler = JsonHandler()

        class MyCustomClass:
            pass

        with pytest.raises(SerializationError) as exc_info:
            handler.serialize(MyCustomClass())
        assert exc_info.value.obj_type == "MyCustomClass"


class TestJsonHandlerDeserialize:
    """Test deserialize method."""

    def test_deserialize_roundtrip_dict(self):
        handler = JsonHandler()
        obj = {"key": "value", "number": 42}
        data = handler.serialize(obj)
        result = handler.deserialize(data)
        assert result == obj

    def test_deserialize_roundtrip_list(self):
        handler = JsonHandler()
        obj = [1, 2, 3, "four"]
        data = handler.serialize(obj)
        result = handler.deserialize(data)
        assert result == obj

    def test_deserialize_roundtrip_nested(self):
        handler = JsonHandler()
        obj = {"nested": {"deep": [1, 2, {"key": "value"}]}}
        data = handler.serialize(obj)
        result = handler.deserialize(data)
        assert result == obj

    def test_deserialize_invalid_json_raises_error(self):
        handler = JsonHandler()
        with pytest.raises(DeserializationError):
            handler.deserialize(b"not valid json")

    def test_deserialize_missing_envelope_raises_error(self):
        handler = JsonHandler()
        # Valid JSON but missing envelope
        data = json.dumps({"key": "value"}).encode("utf-8")
        with pytest.raises(DeserializationError):
            handler.deserialize(data)


class TestJsonHandlerToFile:
    """Test to_file method."""

    def test_to_file_creates_file(self):
        handler = JsonHandler()
        obj = {"key": "value"}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            handler.to_file(obj, path)
            assert path.exists()

    def test_to_file_roundtrip(self):
        handler = JsonHandler()
        obj = {"nested": {"data": [1, 2, 3]}}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            handler.to_file(obj, path)
            result = handler.from_file(path)
            assert result == obj


class TestJsonHandlerFromFile:
    """Test from_file method."""

    def test_from_file_reads_correctly(self):
        handler = JsonHandler()
        obj = {"test": "data"}
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.json"
            handler.to_file(obj, path)
            result = handler.from_file(path)
            assert result == obj

    def test_from_file_nonexistent_raises_error(self):
        handler = JsonHandler()
        with pytest.raises(DeserializationError):
            handler.from_file(Path("/nonexistent/path.json"))

    def test_from_file_invalid_json_raises_error(self):
        handler = JsonHandler()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.json"
            path.write_text("not valid json")
            with pytest.raises(DeserializationError):
                handler.from_file(path)
