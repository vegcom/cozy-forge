#!/usr/bin/env python3
"""
Project setup utility script.
Provides common setup commands for development.
"""

import argparse
import subprocess
import sys
from pathlib import Path


def run_command(cmd, cwd=None):
    """Run a shell command."""
    try:
        subprocess.run(cmd, shell=True, check=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"Command failed: {cmd}")
        sys.exit(e.returncode)


def setup_environment():
    """Set up the development environment."""
    print("Setting up development environment...")

    # Create conda environment
    if Path("environment.yml").exists():
        run_command("conda env create -f environment.yml")
        print("✓ Conda environment created")
    else:
        print("No environment.yml found, skipping conda setup")

    # Install Python dependencies
    if Path("pyproject.toml").exists():
        run_command("pip install -e .")
        print("✓ Python dependencies installed")

    # Install Node.js dependencies
    if Path("package.json").exists():
        run_command("npm install")
        print("✓ Node.js dependencies installed")

    print("Environment setup complete!")


def clean():
    """Clean build artifacts and caches."""
    print("Cleaning build artifacts...")

    patterns = [
        "__pycache__",
        "*.pyc",
        "*.pyo",
        ".pytest_cache",
        ".coverage",
        "node_modules",
        "dist",
        "build",
        "*.egg-info"
    ]

    for pattern in patterns:
        run_command(f"find . -name '{pattern}' -type d -exec rm -rf {{}} + 2>/dev/null || true")
        run_command(f"find . -name '{pattern}' -type f -delete 2>/dev/null || true")

    print("✓ Cleanup complete")


def lint():
    """Run linting tools."""
    print("Running linters...")

    if Path("pyproject.toml").exists():
        run_command("ruff check .")
        run_command("ruff format --check .")
        print("✓ Python linting complete")

    if Path("package.json").exists():
        run_command("npm run lint")
        print("✓ JavaScript linting complete")


def test():
    """Run tests."""
    print("Running tests...")

    if Path("pyproject.toml").exists():
        run_command("python -m pytest")
    else:
        print("No test framework configured")

    print("✓ Tests complete")


def main():
    parser = argparse.ArgumentParser(description="Project setup utility")
    parser.add_argument(
        "command",
        choices=["setup", "clean", "lint", "test"],
        help="Command to run"
    )

    args = parser.parse_args()

    if args.command == "setup":
        setup_environment()
    elif args.command == "clean":
        clean()
    elif args.command == "lint":
        lint()
    elif args.command == "test":
        test()


if __name__ == "__main__":
    main()