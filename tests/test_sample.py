"""Sample test to verify pytest is working."""

from python_repo_template import __version__


def test_version():
    """Verify package version is defined."""
    assert __version__ == "0.1.0"
