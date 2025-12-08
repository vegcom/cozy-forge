#!/usr/bin/env python3
"""
Container startup script.
Replaces bash -c commands in devcontainer.json and docker-compose.yml.
"""

import os
import subprocess
import sys
from pathlib import Path


class Colors:
    """ANSI color codes."""

    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    RED = "\033[0;31m"
    NC = "\033[0m"


def log_success(message: str) -> None:
    """Log success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")


def log_info(message: str) -> None:
    """Log info message."""
    print(f"{Colors.YELLOW}ℹ{Colors.NC} {message}")


def log_error(message: str) -> None:
    """Log error message."""
    print(f"{Colors.RED}✗{Colors.NC} {message}", file=sys.stderr)


def run_command(cmd: str, shell: bool = True, check: bool = True) -> subprocess.CompletedProcess:
    """
    Run a shell command.

    Args:
        cmd: Command to run
        shell: Whether to use shell
        check: Whether to check return code

    Returns:
        CompletedProcess object
    """
    return subprocess.run(cmd, shell=shell, check=check, executable="/bin/bash")  # noqa: DUO116 - Dev container helper


def setup_mounts() -> bool:
    """Run the mount setup script."""
    log_info("Setting up mounts...")
    try:
        result = subprocess.run(
            [sys.executable, "/usr/local/bin/setup_mounts.py"],
            check=True,
        )
        return result.returncode == 0
    except subprocess.CalledProcessError as e:
        log_error(f"Mount setup failed: {e}")
        return False


def activate_venv() -> None:
    """Activate Python virtual environment."""
    venv_path = Path.home() / ".venv"
    if venv_path.exists():
        # Update environment variables for this process
        os.environ["VIRTUAL_ENV"] = str(venv_path)
        os.environ["PATH"] = f"{venv_path}/bin:{os.environ.get('PATH', '')}"
        log_success("Virtual environment activated")
    else:
        log_error("Virtual environment not found")


def upgrade_pip() -> bool:
    """Upgrade pip to latest version."""
    log_info("Upgrading pip...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
        )
        log_success("Pip upgraded")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to upgrade pip: {e}")
        return False


def install_project_dependencies() -> bool:
    """Install project dependencies from pyproject.toml."""
    pyproject = Path("/workspaces/{{ cookiecutter.project_slug }}/pyproject.toml")

    if not pyproject.exists():
        log_info("No pyproject.toml found, skipping dependency installation")
        return True

    log_info("Installing project dependencies...")
    try:
        # Try to install with dev dependencies
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-e", ".[dev]"],
            cwd="/workspaces/{{ cookiecutter.project_slug }}",
            check=True,
            capture_output=True,
        )
        log_success("Project dependencies installed")
        return True
    except subprocess.CalledProcessError:
        # Try without dev dependencies
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-e", "."],
                cwd="/workspaces/{{ cookiecutter.project_slug }}",
                check=True,
                capture_output=True,
            )
            log_success("Project dependencies installed (no dev extras)")
            return True
        except subprocess.CalledProcessError:
            log_info("No dev dependencies defined or installation failed")
            return True  # Don't fail the startup


def install_precommit_hooks() -> bool:
    """Install pre-commit hooks."""
    log_info("Installing pre-commit hooks...")
    try:
        subprocess.run(
            ["pre-commit", "install", "--install-hooks"],
            cwd="/workspaces/{{ cookiecutter.project_slug }}",
            check=True,
            capture_output=True,
        )
        log_success("Pre-commit hooks installed")
        return True
    except subprocess.CalledProcessError as e:
        log_error(f"Failed to install pre-commit hooks: {e}")
        return False


def main() -> int:
    """Main entry point."""
    print("\n🚀 Starting development environment...\n")

    # Run setup steps
    if not setup_mounts():
        log_error("Mount setup failed")
        return 1

    activate_venv()

    if not upgrade_pip():
        log_error("Pip upgrade failed")
        return 1

    if not install_project_dependencies():
        log_error("Dependency installation failed")
        return 1

    if not install_precommit_hooks():
        log_error("Pre-commit hook installation failed")
        return 1

    print()
    log_success("Dev container ready! Run 'terraform init' to get started.")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
