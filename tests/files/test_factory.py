"""Tests for FileHandlerFactory."""

from pathlib import Path

import numpy as np
import pytest

from files_api.files.factory import FileHandlerFactory
from files_api.files.handlers.json_handler import JsonHandler
from files_api.files.handlers.numpy_handler import NumpyHandler


class TestFileHandlerFactoryForObject:
    """Test get_handler_for_object method."""

    def test_numpy_ndarray_returns_numpy_handler(self):
        factory = FileHandlerFactory()
        obj = np.array([1, 2, 3])
        handler = factory.get_handler_for_object(obj)
        assert isinstance(handler, NumpyHandler)

    def test_numpy_2d_array_returns_numpy_handler(self):
        factory = FileHandlerFactory()
        obj = np.zeros((3, 3))
        handler = factory.get_handler_for_object(obj)
        assert isinstance(handler, NumpyHandler)

    def test_numpy_scalar_float64_returns_json_handler(self):
        """Numpy scalars are not ndarrays, so they go to JSON."""
        factory = FileHandlerFactory()
        obj = np.float64(3.14)
        handler = factory.get_handler_for_object(obj)
        assert isinstance(handler, JsonHandler)

    def test_numpy_scalar_int32_returns_json_handler(self):
        """Numpy scalars are not ndarrays, so they go to JSON."""
        factory = FileHandlerFactory()
        obj = np.int32(42)
        handler = factory.get_handler_for_object(obj)
        assert isinstance(handler, JsonHandler)

    def test_dict_returns_json_handler(self):
        factory = FileHandlerFactory()
        obj = {"key": "value"}
        handler = factory.get_handler_for_object(obj)
        assert isinstance(handler, JsonHandler)

    def test_list_returns_json_handler(self):
        factory = FileHandlerFactory()
        obj = [1, 2, 3]
        handler = factory.get_handler_for_object(obj)
        assert isinstance(handler, JsonHandler)

    def test_string_returns_json_handler(self):
        factory = FileHandlerFactory()
        obj = "hello"
        handler = factory.get_handler_for_object(obj)
        assert isinstance(handler, JsonHandler)

    def test_int_returns_json_handler(self):
        factory = FileHandlerFactory()
        obj = 42
        handler = factory.get_handler_for_object(obj)
        assert isinstance(handler, JsonHandler)

    def test_nested_dict_returns_json_handler(self):
        factory = FileHandlerFactory()
        obj = {"nested": {"deep": [1, 2, 3]}}
        handler = factory.get_handler_for_object(obj)
        assert isinstance(handler, JsonHandler)


class TestFileHandlerFactoryForFile:
    """Test get_handler_for_file method."""

    def test_npy_extension_returns_numpy_handler(self):
        factory = FileHandlerFactory()
        path = Path("/some/path/file.npy")
        handler = factory.get_handler_for_file(path)
        assert isinstance(handler, NumpyHandler)

    def test_json_extension_returns_json_handler(self):
        factory = FileHandlerFactory()
        path = Path("/some/path/file.json")
        handler = factory.get_handler_for_file(path)
        assert isinstance(handler, JsonHandler)

    def test_unknown_extension_raises_error(self):
        factory = FileHandlerFactory()
        path = Path("/some/path/file.xyz")
        with pytest.raises(ValueError, match="Unknown file extension"):
            factory.get_handler_for_file(path)

    def test_no_extension_raises_error(self):
        factory = FileHandlerFactory()
        path = Path("/some/path/file")
        with pytest.raises(ValueError, match="Unknown file extension"):
            factory.get_handler_for_file(path)


class TestFileHandlerFactoryHandlerCaching:
    """Test that factory returns consistent handler instances."""

    def test_same_handler_type_for_same_object_type(self):
        factory = FileHandlerFactory()
        handler1 = factory.get_handler_for_object(np.array([1]))
        handler2 = factory.get_handler_for_object(np.array([2, 3]))
        assert type(handler1) == type(handler2)

    def test_same_handler_type_for_same_extension(self):
        factory = FileHandlerFactory()
        handler1 = factory.get_handler_for_file(Path("a.npy"))
        handler2 = factory.get_handler_for_file(Path("b.npy"))
        assert type(handler1) == type(handler2)
