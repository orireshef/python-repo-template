"""Integration tests for the files API."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from files_api.files import (
    FileExistsError,
    FileNotFoundError,
    IFileSystem,
    LocalFileSystem,
    SerializationError,
)


class TestFullRoundTrip:
    """Test complete save/get cycles."""

    def test_save_and_get_numpy_array(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)

            # Save numpy array
            original = np.array([[1.5, 2.5, 3.5], [4.5, 5.5, 6.5]])
            fs.save("matrix", original)

            # Verify file was created with correct extension
            assert (Path(tmpdir) / "matrix.npy").exists()

            # Get and verify
            result = fs.get("matrix")
            np.testing.assert_array_equal(result, original)
            assert result.dtype == original.dtype

    def test_save_and_get_dict(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)

            # Save dict
            original = {
                "name": "test",
                "values": [1, 2, 3],
                "nested": {"key": "value"},
            }
            fs.save("config", original)

            # Verify file was created with correct extension
            assert (Path(tmpdir) / "config.json").exists()

            # Get and verify
            result = fs.get("config")
            assert result == original

    def test_save_and_get_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)

            original = [1, "two", 3.0, None, True]
            fs.save("items", original)
            result = fs.get("items")
            assert result == original

    def test_mixed_types_in_same_filesystem(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)

            # Save different types
            fs.save("array", np.zeros((10, 10)))
            fs.save("config", {"setting": True})
            fs.save("items", [1, 2, 3])

            # Verify count
            assert fs.count() == 3

            # Verify all can be retrieved
            assert fs.get("array").shape == (10, 10)
            assert fs.get("config") == {"setting": True}
            assert fs.get("items") == [1, 2, 3]


class TestErrorHandling:
    """Test error scenarios."""

    def test_file_collision_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)

            fs.save("data", {"key": "value"})

            with pytest.raises(FileExistsError) as exc_info:
                fs.save("data", {"other": "value"})

            assert "data" in str(exc_info.value)

    def test_get_nonexistent_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)

            with pytest.raises(FileNotFoundError) as exc_info:
                fs.get("missing")

            assert "missing" in str(exc_info.value)

    def test_non_serializable_object_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)

            class NotSerializable:
                pass

            with pytest.raises(SerializationError) as exc_info:
                fs.save("bad", NotSerializable())

            assert "NotSerializable" in str(exc_info.value)


class TestExistsAndCount:
    """Test exists and count operations."""

    def test_exists_after_save(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)

            assert fs.exists("data") is False
            fs.save("data", {"key": "value"})
            assert fs.exists("data") is True

    def test_count_with_prefix_filter(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)

            fs.save("user_alice", {"name": "Alice"})
            fs.save("user_bob", {"name": "Bob"})
            fs.save("config", {"setting": True})
            fs.save("user_charlie", {"name": "Charlie"})

            assert fs.count() == 4
            assert fs.count("user_") == 3
            assert fs.count("config") == 1
            assert fs.count("nonexistent_") == 0


class TestInterfaceCompliance:
    """Test that LocalFileSystem properly implements IFileSystem."""

    def test_is_instance_of_ifilesystem(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            assert isinstance(fs, IFileSystem)

    def test_all_interface_methods_exist(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            assert hasattr(fs, "save")
            assert hasattr(fs, "get")
            assert hasattr(fs, "count")
            assert hasattr(fs, "exists")
            assert callable(fs.save)
            assert callable(fs.get)
            assert callable(fs.count)
            assert callable(fs.exists)
