#!/usr/bin/env python3
"""
Setup script to handle optional mounts and config files.
Works on both Linux and Windows (WSL/Git Bash).
"""

import os
import platform
import shutil
import sys
from pathlib import Path
from typing import Optional


class Colors:
    """ANSI color codes for terminal output."""

    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    RED = "\033[0;31m"
    NC = "\033[0m"  # No Color


def log_success(message: str) -> None:
    """Log a success message."""
    print(f"{Colors.GREEN}✓{Colors.NC} {message}")


def log_info(message: str) -> None:
    """Log an info message."""
    print(f"{Colors.YELLOW}ℹ{Colors.NC} {message}")


def log_debug(message: str) -> None:
    """Log a debug message."""
    print(f"{Colors.BLUE}→{Colors.NC} {message}")


def log_error(message: str) -> None:
    """Log an error message."""
    print(f"{Colors.RED}✗{Colors.NC} {message}", file=sys.stderr)


def detect_os() -> str:
    """Detect the operating system."""
    system = platform.system()
    if system == "Linux":
        os_type = "Linux"
    elif system == "Darwin":
        os_type = "Mac"
    elif system == "Windows":
        os_type = "Windows"
    else:
        os_type = "Unknown"

    log_debug(f"Detected OS: {os_type}")
    return os_type


def copy_file_safe(src: Path, dest: Path, mode: Optional[int] = None) -> bool:
    """
    Safely copy a file from source to destination.

    Args:
        src: Source file path
        dest: Destination file path
        mode: Optional file permission mode (e.g., 0o600)

    Returns:
        True if successful, False otherwise
    """
    try:
        if not src.exists():
            return False

        # Create parent directory if it doesn't exist
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(src, dest)

        # Set permissions if specified
        if mode is not None:
            dest.chmod(mode)

        return True
    except Exception as e:
        log_error(f"Failed to copy {src} to {dest}: {e}")
        return False


def copy_directory_safe(src: Path, dest: Path) -> bool:
    """
    Safely copy a directory from source to destination.

    Args:
        src: Source directory path
        dest: Destination directory path

    Returns:
        True if successful, False otherwise
    """
    try:
        if not src.exists() or not src.is_dir():
            return False

        # Create destination directory
        dest.mkdir(parents=True, exist_ok=True)

        # Copy all files
        for item in src.iterdir():
            if item.is_file():
                dest_file = dest / item.name
                shutil.copy2(item, dest_file)

                # Set appropriate permissions for SSH keys
                if item.suffix == "" and item.name.startswith("id_"):
                    # Private key
                    dest_file.chmod(0o600)
                elif item.suffix == ".pub":
                    # Public key
                    dest_file.chmod(0o644)

        return True
    except Exception as e:
        log_error(f"Failed to copy directory {src} to {dest}: {e}")
        return False


def setup_kubeconfig() -> None:
    """Setup kubeconfig from host or environment."""
    home = Path.home()
    kube_dir = home / ".kube"
    kube_config = kube_dir / "config"

    # Check for KUBECONFIG environment variable
    kubeconfig_host = os.environ.get("KUBECONFIG_HOST")
    if kubeconfig_host:
        src = Path(kubeconfig_host)
        if copy_file_safe(src, kube_config, mode=0o600):
            log_success(f"Kubeconfig copied from {src}")
            return

    # Check for mounted host kubeconfig
    host_kube = Path("/mnt/host-kube/config")
    if host_kube.exists():
        if copy_file_safe(host_kube, kube_config, mode=0o600):
            log_success("Kubeconfig copied from host mount")
            return

    # Check if config already exists
    if kube_config.exists():
        log_success("Kubeconfig already exists")
    else:
        log_info("No kubeconfig found. Configure kubectl manually or mount ~/.kube/config")


def setup_ssh_keys() -> None:
    """Setup SSH keys from host mount."""
    home = Path.home()
    ssh_dir = home / ".ssh"
    host_ssh = Path("/mnt/host-ssh")

    if host_ssh.exists() and any(host_ssh.iterdir()):
        if copy_directory_safe(host_ssh, ssh_dir):
            ssh_dir.chmod(0o700)
            log_success("SSH keys copied from host mount")
            return

    if ssh_dir.exists() and any(ssh_dir.iterdir()):
        log_success("SSH keys already exist")
    else:
        log_info("No SSH keys found. Generate them with: ssh-keygen -t ed25519 -C 'your_email@example.com'")


def setup_gitconfig() -> None:
    """Setup git configuration from host mount."""
    home = Path.home()
    gitconfig = home / ".gitconfig"
    host_gitconfig = Path("/mnt/host-gitconfig")

    if host_gitconfig.exists():
        if copy_file_safe(host_gitconfig, gitconfig):
            log_success("Git config copied from host mount")
            return

    if gitconfig.exists():
        log_success("Git config already exists")
    else:
        log_info("No git config found. Setting basic defaults...")
        os.system("git config --global init.defaultBranch main")  # noqa: DUO106 - Dev container setup
        os.system("git config --global pull.rebase false")  # noqa: DUO106 - Dev container setup
        log_success("Basic git config created")


def setup_env_file() -> None:
    """Setup .env file from host mount or workspace."""
    workspace = Path("/workspaces/{{ cookiecutter.project_slug }}")
    env_file = workspace / ".env"
    host_env = Path("/mnt/host-env")

    if env_file.exists():
        log_success(".env file found in workspace")
    elif host_env.exists():
        try:
            # Create symlink to host env file
            env_file.symlink_to(host_env)
            log_success(".env linked from host")
        except Exception as e:
            log_error(f"Failed to link .env: {e}")
    else:
        log_info("No .env file found. Create one if needed for secrets.")


def setup_terraform_tfvars() -> None:
    """Setup terraform.tfvars from host mount or workspace."""
    workspace = Path("/workspaces/{{ cookiecutter.project_slug }}")
    terraform_dir = workspace / "terraform"
    tfvars = terraform_dir / "terraform.tfvars"
    host_tfvars = Path("/mnt/host-tfvars")

    if tfvars.exists():
        log_success("terraform.tfvars found in workspace")
    elif host_tfvars.exists():
        try:
            # Create terraform directory if it doesn't exist
            terraform_dir.mkdir(parents=True, exist_ok=True)

            # Create symlink to host tfvars file
            tfvars.symlink_to(host_tfvars)
            log_success("terraform.tfvars linked from host")
        except Exception as e:
            log_error(f"Failed to link terraform.tfvars: {e}")
    else:
        log_info("No terraform.tfvars found. Copy from terraform.tfvars.example if needed.")


def main() -> int:
    """Main entry point."""
    print("\n🔧 Setting up development environment...\n")

    # Detect OS
    detect_os()
    print()

    # Setup configurations
    setup_kubeconfig()
    setup_ssh_keys()
    setup_gitconfig()
    setup_env_file()
    setup_terraform_tfvars()

    print()
    log_success("Mount setup complete!")
    print()

    return 0


if __name__ == "__main__":
    sys.exit(main())
