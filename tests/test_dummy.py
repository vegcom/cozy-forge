"""Smoke tests — verifies the template stub is importable."""

from cozy_forge import __version__


def test_placeholder() -> None:
  assert True


def test_import() -> None:
  assert __version__ == "0.0.0"
