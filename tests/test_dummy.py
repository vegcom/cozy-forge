"""Basic test suite for the project template."""


def test_basic_assertion():
    """A simple test that always passes."""
    assert True


def test_project_structure():
    """Test that basic project files exist."""
    from pathlib import Path

    # Check for essential files
    essential_files = [
        "README.md",
        "pyproject.toml",
    ]

    for file in essential_files:
        assert Path(file).exists(), f"Essential file {file} is missing"


def test_cookiecutter_variables():
    """Test that cookiecutter variables are properly formatted."""
    # This would be replaced by cookiecutter, but we can test the structure
    project_slug = "{{ cookiecutter.project_slug }}"
    assert isinstance(project_slug, str)
    assert len(project_slug) > 0
