"""Tests for NumpyHandler."""

import tempfile
from io import BytesIO
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


class TestNumpyHandlerToFile:
    """Test to_file method with file-like objects."""

    def test_to_file_1d_array(self):
        handler = NumpyHandler()
        arr = np.array([1, 2, 3])
        buffer = BytesIO()
        handler.to_file(arr, buffer)
        assert buffer.tell() > 0  # Data was written

    def test_to_file_2d_array(self):
        handler = NumpyHandler()
        arr = np.array([[1, 2], [3, 4]])
        buffer = BytesIO()
        handler.to_file(arr, buffer)
        assert buffer.tell() > 0

    def test_to_file_nd_array(self):
        handler = NumpyHandler()
        arr = np.zeros((2, 3, 4, 5))
        buffer = BytesIO()
        handler.to_file(arr, buffer)
        assert buffer.tell() > 0

    def test_to_file_different_dtypes(self):
        handler = NumpyHandler()
        for dtype in [np.float64, np.int32, np.bool_, np.complex128]:
            arr = np.array([1, 2, 3], dtype=dtype)
            buffer = BytesIO()
            handler.to_file(arr, buffer)
            assert buffer.tell() > 0

    def test_to_file_empty_array(self):
        handler = NumpyHandler()
        arr = np.array([])
        buffer = BytesIO()
        handler.to_file(arr, buffer)
        assert buffer.tell() > 0

    def test_to_file_with_real_file(self):
        handler = NumpyHandler()
        arr = np.array([1, 2, 3])
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.npy"
            with open(path, "wb") as f:
                handler.to_file(arr, f)
            assert path.exists()
            assert path.stat().st_size > 0


class TestNumpyHandlerFromFile:
    """Test from_file method with file-like objects."""

    def test_from_file_roundtrip_1d(self):
        handler = NumpyHandler()
        arr = np.array([1.0, 2.0, 3.0])
        buffer = BytesIO()
        handler.to_file(arr, buffer)
        buffer.seek(0)
        result = handler.from_file(buffer)
        np.testing.assert_array_equal(result, arr)

    def test_from_file_roundtrip_2d(self):
        handler = NumpyHandler()
        arr = np.array([[1, 2], [3, 4]])
        buffer = BytesIO()
        handler.to_file(arr, buffer)
        buffer.seek(0)
        result = handler.from_file(buffer)
        np.testing.assert_array_equal(result, arr)

    def test_from_file_preserves_dtype(self):
        handler = NumpyHandler()
        arr = np.array([1, 2, 3], dtype=np.int32)
        buffer = BytesIO()
        handler.to_file(arr, buffer)
        buffer.seek(0)
        result = handler.from_file(buffer)
        assert result.dtype == np.int32

    def test_from_file_invalid_data_raises_error(self):
        handler = NumpyHandler()
        buffer = BytesIO(b"not valid npy data")
        with pytest.raises(DeserializationError):
            handler.from_file(buffer)

    def test_from_file_with_real_file(self):
        handler = NumpyHandler()
        arr = np.array([10, 20, 30])
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "test.npy"
            with open(path, "wb") as f:
                handler.to_file(arr, f)
            with open(path, "rb") as f:
                result = handler.from_file(f)
            np.testing.assert_array_equal(result, arr)


class TestNumpyHandlerObjectArrays:
    """Test object arrays (with pickle)."""

    def test_object_array_roundtrip(self):
        handler = NumpyHandler()
        arr = np.array([{"key": "value"}, {"other": 123}], dtype=object)
        buffer = BytesIO()
        handler.to_file(arr, buffer)
        buffer.seek(0)
        result = handler.from_file(buffer)
        assert result[0] == {"key": "value"}
        assert result[1] == {"other": 123}
