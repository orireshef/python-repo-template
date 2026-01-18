"""Tests for LocalFileSystem."""

import tempfile
from pathlib import Path

import numpy as np
import pytest

from files_api.files.exceptions import FileExistsError, FileNotFoundError
from files_api.files.local import LocalFileSystem


class TestLocalFileSystemInit:
    """Test initialization."""

    def test_creates_base_directory(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            base_path = Path(tmpdir) / "new_dir"
            assert not base_path.exists()
            LocalFileSystem(base_path)
            assert base_path.exists()

    def test_accepts_string_path(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            assert fs.base_path == Path(tmpdir)

    def test_accepts_path_object(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir)
            fs = LocalFileSystem(path)
            assert fs.base_path == path


class TestLocalFileSystemSave:
    """Test save method."""

    def test_save_dict_creates_json_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("config", {"key": "value"})
            assert (Path(tmpdir) / "config.json").exists()

    def test_save_numpy_creates_npy_file(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("array", np.array([1, 2, 3]))
            assert (Path(tmpdir) / "array.npy").exists()

    def test_save_same_key_twice_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("data", {"key": "value"})
            with pytest.raises(FileExistsError) as exc_info:
                fs.save("data", {"other": "data"})
            assert "data" in str(exc_info.value)

    def test_save_key_collision_different_types_raises_error(self):
        """Same key with different types should still raise error."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("mydata", {"key": "value"})  # Creates mydata.json
            with pytest.raises(FileExistsError):
                fs.save("mydata", np.array([1, 2, 3]))  # Would create mydata.npy

    def test_save_list(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("items", [1, 2, 3])
            assert (Path(tmpdir) / "items.json").exists()


class TestLocalFileSystemGet:
    """Test get method."""

    def test_get_dict_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            original = {"key": "value", "number": 42}
            fs.save("config", original)
            result = fs.get("config")
            assert result == original

    def test_get_numpy_roundtrip(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            original = np.array([[1, 2], [3, 4]])
            fs.save("matrix", original)
            result = fs.get("matrix")
            np.testing.assert_array_equal(result, original)

    def test_get_nonexistent_key_raises_error(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            with pytest.raises(FileNotFoundError) as exc_info:
                fs.get("nonexistent")
            assert "nonexistent" in str(exc_info.value)

    def test_get_nested_structure(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            original = {"nested": {"deep": [1, 2, {"key": "value"}]}}
            fs.save("nested", original)
            result = fs.get("nested")
            assert result == original


class TestLocalFileSystemCount:
    """Test count method."""

    def test_count_empty_returns_zero(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            assert fs.count() == 0

    def test_count_all_files(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("file1", {"a": 1})
            fs.save("file2", {"b": 2})
            fs.save("file3", np.array([1]))
            assert fs.count() == 3

    def test_count_with_prefix(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("data_a", {"a": 1})
            fs.save("data_b", {"b": 2})
            fs.save("other", {"c": 3})
            assert fs.count("data_") == 2

    def test_count_prefix_no_matches(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("file1", {"a": 1})
            assert fs.count("nonexistent_") == 0


class TestLocalFileSystemOpen:
    """Test _open method (internal file-like object provider)."""

    def test_open_returns_writable_file_object(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            with fs._open("test.txt", "wb") as f:
                f.write(b"hello")
            assert (Path(tmpdir) / "test.txt").exists()
            assert (Path(tmpdir) / "test.txt").read_bytes() == b"hello"

    def test_open_returns_readable_file_object(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            # Create file first
            (Path(tmpdir) / "test.txt").write_bytes(b"world")
            # Read via _open
            with fs._open("test.txt", "rb") as f:
                content = f.read()
            assert content == b"world"


class TestLocalFileSystemExists:
    """Test exists method."""

    def test_exists_returns_true_for_existing_json(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("config", {"key": "value"})
            assert fs.exists("config") is True

    def test_exists_returns_true_for_existing_npy(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("array", np.array([1, 2, 3]))
            assert fs.exists("array") is True

    def test_exists_returns_false_for_nonexistent(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            assert fs.exists("nonexistent") is False

    def test_exists_key_without_extension(self):
        """Key should work without specifying extension."""
        with tempfile.TemporaryDirectory() as tmpdir:
            fs = LocalFileSystem(tmpdir)
            fs.save("myfile", {"data": 1})
            assert fs.exists("myfile") is True
            assert fs.exists("myfile.json") is False  # Full path shouldn't match
