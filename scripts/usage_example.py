#!/usr/bin/env python
"""Usage example for the Files API.

This script demonstrates how to use the LocalFileSystem to save and retrieve
different types of data with automatic format selection.

Run with: uv run python scripts/usage_example.py
       or: uv run python scripts/usage_example.py --debug  (for verbose logging)
"""

import logging
import sys
import tempfile
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

import numpy as np

from files_api.files import LocalFileSystem


def main():
    # Enable debug logging if --debug flag is passed
    if "--debug" in sys.argv:
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(levelname)s:%(name)s:%(message)s",
        )
        print("Debug logging enabled\n")

    # Create a temporary directory for this example
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Using temporary directory: {tmpdir}\n")

        # Initialize the filesystem
        fs = LocalFileSystem(tmpdir)

        # ============================================================
        # Example 1: Save and retrieve a numpy array
        # ============================================================
        print("=" * 60)
        print("Example 1: Numpy Arrays")
        print("=" * 60)

        matrix = np.array([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0]])
        fs.save("my_matrix", matrix)
        print(f"Saved numpy array with shape {matrix.shape}")
        print(f"File created: {list(Path(tmpdir).glob('my_matrix.*'))}")

        loaded_matrix = fs.get("my_matrix")
        print(f"Loaded array:\n{loaded_matrix}")
        print(f"Arrays equal: {np.array_equal(matrix, loaded_matrix)}\n")

        # ============================================================
        # Example 2: Save and retrieve a dictionary (JSON)
        # ============================================================
        print("=" * 60)
        print("Example 2: Dictionaries (JSON)")
        print("=" * 60)

        config = {
            "name": "my_project",
            "version": "1.0.0",
            "settings": {"debug": True, "max_workers": 4},
            "tags": ["python", "data", "files"],
        }
        fs.save("config", config)
        print("Saved config dictionary")
        print(f"File created: {list(Path(tmpdir).glob('config.*'))}")

        loaded_config = fs.get("config")
        print(f"Loaded config: {loaded_config}")
        print(f"Configs equal: {config == loaded_config}\n")

        # ============================================================
        # Example 3: Save and retrieve a list
        # ============================================================
        print("=" * 60)
        print("Example 3: Lists")
        print("=" * 60)

        items = [1, "two", 3.0, None, True, {"nested": "dict"}]
        fs.save("items", items)
        print(f"Saved list with {len(items)} items")

        loaded_items = fs.get("items")
        print(f"Loaded items: {loaded_items}\n")

        # ============================================================
        # Example 4: Check existence and count
        # ============================================================
        print("=" * 60)
        print("Example 4: Existence and Count")
        print("=" * 60)

        print(f"'my_matrix' exists: {fs.exists('my_matrix')}")
        print(f"'nonexistent' exists: {fs.exists('nonexistent')}")
        print(f"Total files: {fs.count()}")

        # Save more files with a prefix
        fs.save("data_train", np.random.rand(100, 10))
        fs.save("data_test", np.random.rand(20, 10))
        fs.save("data_val", np.random.rand(10, 10))

        print(f"Files with 'data_' prefix: {fs.count('data_')}")
        print(f"Total files now: {fs.count()}\n")

        # ============================================================
        # Example 5: Object arrays (with pickle)
        # ============================================================
        print("=" * 60)
        print("Example 5: Object Arrays")
        print("=" * 60)

        # Arrays containing Python objects
        object_array = np.array(
            [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}], dtype=object
        )
        fs.save("people", object_array)
        print(f"Saved object array with dtype={object_array.dtype}")

        loaded_people = fs.get("people")
        print(f"Loaded: {loaded_people}")
        print(f"First person: {loaded_people[0]}\n")

        # ============================================================
        # Summary
        # ============================================================
        print("=" * 60)
        print("Summary")
        print("=" * 60)
        print(f"Files in storage: {fs.count()}")
        for ext in [".npy", ".json"]:
            files = list(Path(tmpdir).glob(f"*{ext}"))
            print(f"  {ext} files: {len(files)}")
            for f in files:
                print(f"    - {f.name}")


if __name__ == "__main__":
    main()
