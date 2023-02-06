"""Package level tests"""
from pttbackend import __version__


def test_version() -> None:
    """Make sure version matches expected"""
    assert __version__ == "1.0.0"
