"""Tests for NumpyHandler."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from files_api.files.exceptions import DeserializationError
from files_api.files.handlers.numpy_handler import NumpyHandler


class TestNumpyHandlerAttributes:
    """Test handler attributes."""

    def test_extension_is_npy(self):
        handler = NumpyHandler()
        assert handler.extension == ".npy"

    def test_type_name_is_numpy(self):
        handler = NumpyHandler()
        assert handler.type_name == "numpy"


class TestNumpyHandlerSerialize:
    """Test serialize method."""

    def test_serialize_1d_array(self):
        handler = NumpyHandler()
        arr = np.array([1, 2, 3])
        result = handler.serialize(arr)
        assert isinstance(result, bytes)
        assert len(result) > 0

    def test_serialize_2d_array(self):
        handler = NumpyHandler()
        arr = np.array([[1, 2], [3, 4]])
        result = handler.serialize(arr)
        assert isinstance(result, bytes)

    def test_serialize_nd_array(self):
        handler = NumpyHandler()
        arr = np.zeros((2, 3, 4, 5))
        result = handler.serialize(arr)
        assert isinstance(result, bytes)

    def test_serialize_different_dtypes(self):
        handler = NumpyHandler()
        for dtype in [np.float64, np.int32, np.bool_, np.complex128]:
            arr = np.array([1, 2, 3], dtype=dtype)
            result = handler.serialize(arr)
            assert isinstance(result, bytes)

    def test_serialize_empty_array(self):
        handler = NumpyHandler()
        arr = np.array([])
        result = handler.serialize(arr)
        assert isinstance(result, bytes)

    def test_serialize_scalar(self):
        handler = NumpyHandler()
        scalar = np.float64(3.14)
        result = handler.serialize(scalar)
        assert isinstance(result, bytes)


class TestNumpyHandlerDeserialize:
    """Test deserialize method."""

    def test_deserialize_roundtrip_1d(self):
        handler = NumpyHandler()
        arr = np.array([1.0, 2.0, 3.0])
        data = handler.serialize(arr)
        result = handler.deserialize(data)
        np.testing.assert_array_equal(result, arr)

    def test_deserialize_roundtrip_2d(self):
        handler = NumpyHandler()
        arr = np.array([[1, 2], [3, 4]])
        data = handler.serialize(arr)
        result = handler.deserialize(data)
        np.testing.assert_array_equal(result, arr)

    def test_deserialize_preserves_dtype(self):
        handler = NumpyHandler()
        arr = np.array([1, 2, 3], dtype=np.int32)
        data = handler.serialize(arr)
        result = handler.deserialize(data)
        assert result.dtype == np.int32

    def test_deserialize_invalid_data_raises_error(self):
        handler = NumpyHandler()
        with pytest.raises(DeserializationError):
            handler.deserialize(b"not valid npy data")


class TestNumpyHandlerToFile:
    """Test to_file method."""

    def test_to_file_creates_file(self):
        handler = NumpyHandler()
        arr = np.array([1, 2, 3])
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.npy"
            handler.to_file(arr, path)
            assert path.exists()

    def test_to_file_roundtrip(self):
        handler = NumpyHandler()
        arr = np.array([[1.5, 2.5], [3.5, 4.5]])
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.npy"
            handler.to_file(arr, path)
            result = handler.from_file(path)
            np.testing.assert_array_equal(result, arr)


class TestNumpyHandlerFromFile:
    """Test from_file method."""

    def test_from_file_reads_correctly(self):
        handler = NumpyHandler()
        arr = np.array([10, 20, 30])
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.npy"
            np.save(path, arr)
            result = handler.from_file(path)
            np.testing.assert_array_equal(result, arr)

    def test_from_file_nonexistent_raises_error(self):
        handler = NumpyHandler()
        with pytest.raises(DeserializationError):
            handler.from_file(Path("/nonexistent/path.npy"))

    def test_from_file_invalid_data_raises_error(self):
        handler = NumpyHandler()
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "invalid.npy"
            path.write_text("not valid npy data")
            with pytest.raises(DeserializationError):
                handler.from_file(path)
