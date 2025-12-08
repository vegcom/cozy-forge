#!/usr/bin/env python3
"""
Dev Container Deployment Manager for {{ cookiecutter.project_slug }}.
Manages Kali-based development environment deployment to Kubernetes.
"""

import argparse
import os
import subprocess
import sys
from pathlib import Path

# Configuration
NAMESPACE = "dev"
DEPLOYMENT_NAME = "{{ cookiecutter.project_slug }}-dev"
SERVICE_NAME = "{{ cookiecutter.project_slug }}-dev-service"
INGRESS_NAME = "{{ cookiecutter.project_slug }}-dev-ingress"
PVC_NAME = "{{ cookiecutter.project_slug }}-dev-workspace"


class Colors:
    """ANSI color codes."""

    RED = "\033[0;31m"
    GREEN = "\033[0;32m"
    YELLOW = "\033[1;33m"
    BLUE = "\033[0;34m"
    NC = "\033[0m"


def log_info(message: str) -> None:
    """Log info message."""
    print(f"{Colors.BLUE}[INFO]{Colors.NC} {message}")


def log_success(message: str) -> None:
    """Log success message."""
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")


def log_warning(message: str) -> None:
    """Log warning message."""
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")


def log_error(message: str) -> None:
    """Log error message."""
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}", file=sys.stderr)


def run_command(
    cmd: list[str],
    check: bool = True,
    capture_output: bool = False,
) -> subprocess.CompletedProcess:
    """
    Run a command and handle errors.

    Args:
        cmd: Command and arguments as list
        check: Whether to check return code
        capture_output: Whether to capture stdout/stderr

    Returns:
        CompletedProcess object
    """
    try:
        return subprocess.run(cmd, check=check, capture_output=capture_output, text=True)
    except subprocess.CalledProcessError:
        if not capture_output:
            log_error(f"Command failed: {' '.join(cmd)}")
        raise


def check_kubectl() -> bool:
    """Check if kubectl is available."""
    try:
        subprocess.run(["kubectl", "version", "--client"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        log_error("kubectl is not installed or not in PATH")
        return False


def check_directory() -> bool:
    """Check if we're in the right directory."""
    dockerfile = Path(".devcontainer/Dockerfile")
    if not dockerfile.exists():
        log_error("Please run this script from the {{ cookiecutter.project_slug }} project root directory")
        return False
    return True


def build_image(skip_push: bool = False) -> int:
    """Build and optionally push the dev container image."""
    log_info("Building Kali-based dev container image...")

    try:
        run_command(["docker", "build", "-f", ".devcontainer/Dockerfile", "-t", "{{ cookiecutter.project_slug }}-dev:latest", "."])

        log_info("Tagging image...")
        registry = os.environ.get("DOCKER_REGISTRY", "your-registry")
        run_command(["docker", "tag", "{{ cookiecutter.project_slug }}-dev:latest", f"{registry}/{{ cookiecutter.project_slug }}-dev:latest"])

        if not skip_push:
            log_info("Pushing image to registry...")
            run_command(["docker", "push", f"{registry}/{{ cookiecutter.project_slug }}-dev:latest"])
            log_success("Dev container image built and pushed")
        else:
            log_success("Dev container image built (push skipped)")

        return 0
    except subprocess.CalledProcessError:
        return 1


def create_namespace() -> int:
    """Create namespace if it doesn't exist."""
    try:
        result = run_command(
            ["kubectl", "get", "namespace", NAMESPACE],
            check=False,
            capture_output=True,
        )

        if result.returncode != 0:
            log_info(f"Creating namespace: {NAMESPACE}")
            run_command(["kubectl", "create", "namespace", NAMESPACE])
        else:
            log_info(f"Namespace {NAMESPACE} already exists")

        return 0
    except subprocess.CalledProcessError:
        return 1


def create_secrets() -> int:
    """Create Kubernetes secrets for config files."""
    log_info("Creating Kubernetes secrets...")
    home = Path.home()

    try:
        # Kubeconfig
        kubeconfig = home / ".kube" / "config"
        if kubeconfig.exists():
            run_command(
                [
                    "kubectl",
                    "create",
                    "secret",
                    "generic",
                    "kube-config",
                    f"--from-file=config={kubeconfig}",
                    f"--namespace={NAMESPACE}",
                    "--dry-run=client",
                    "-o",
                    "yaml",
                ],
                capture_output=True,
            )
            # Apply the secret
            result = subprocess.run(
                [
                    "kubectl",
                    "create",
                    "secret",
                    "generic",
                    "kube-config",
                    f"--from-file=config={kubeconfig}",
                    f"--namespace={NAMESPACE}",
                    "--dry-run=client",
                    "-o",
                    "yaml",
                ],
                capture_output=True,
                text=True,
            )
            subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout, text=True)
            log_success("Kubeconfig secret created")
        else:
            log_warning(f"No kubeconfig found at {kubeconfig}")

        # SSH keys
        ssh_keys = [
            (home / ".ssh" / "id_rsa", home / ".ssh" / "id_rsa.pub"),
            (home / ".ssh" / "id_ed25519", home / ".ssh" / "id_ed25519.pub"),
        ]

        for private_key, public_key in ssh_keys:
            if private_key.exists() and public_key.exists():
                result = subprocess.run(
                    [
                        "kubectl",
                        "create",
                        "secret",
                        "generic",
                        "ssh-keys",
                        f"--from-file={private_key.name}={private_key}",
                        f"--from-file={public_key.name}={public_key}",
                        f"--namespace={NAMESPACE}",
                        "--dry-run=client",
                        "-o",
                        "yaml",
                    ],
                    capture_output=True,
                    text=True,
                )
                subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout, text=True)
                log_success("SSH keys secret created")
                break
        else:
            log_warning("No SSH keys found at ~/.ssh/")

        # Git config
        gitconfig = home / ".gitconfig"
        if gitconfig.exists():
            result = subprocess.run(
                [
                    "kubectl",
                    "create",
                    "secret",
                    "generic",
                    "git-config",
                    f"--from-file=.gitconfig={gitconfig}",
                    f"--namespace={NAMESPACE}",
                    "--dry-run=client",
                    "-o",
                    "yaml",
                ],
                capture_output=True,
                text=True,
            )
            subprocess.run(["kubectl", "apply", "-f", "-"], input=result.stdout, text=True)
            log_success("Git config secret created")

        return 0
    except subprocess.CalledProcessError:
        return 1


def deploy() -> int:
    """Deploy the dev environment."""
    log_info("Deploying dev environment to Kubernetes...")

    deployment_yaml = Path(".devcontainer/dev-deployment.yaml")
    if not deployment_yaml.exists():
        log_warning("No dev-deployment.yaml found. Please create one or deploy manually.")
        return 1

    try:
        run_command(["kubectl", "apply", "-f", str(deployment_yaml)])

        log_info("Waiting for deployment to be ready...")
        # Try deployment first
        result = subprocess.run(
            [
                "kubectl",
                "wait",
                "--for=condition=available",
                "--timeout=300s",
                f"deployment/{DEPLOYMENT_NAME}",
                "-n",
                NAMESPACE,
            ],
            capture_output=True,
        )

        if result.returncode != 0:
            # Fall back to pod wait
            run_command([
                "kubectl",
                "wait",
                "--for=condition=ready",
                "--timeout=300s",
                "pod",
                f"-l app={DEPLOYMENT_NAME}",
                "-n",
                NAMESPACE,
            ])

        log_success("Dev environment deployed successfully!")
        return 0
    except subprocess.CalledProcessError:
        return 1


def status() -> int:
    """Show deployment status."""
    log_info("Dev environment status:")
    print()

    # Pods
    result = subprocess.run(
        ["kubectl", "get", "pods", "-n", NAMESPACE, f"-l app={DEPLOYMENT_NAME}"],
        capture_output=True,
    )
    if result.returncode == 0:
        print(result.stdout.decode())
    else:
        print(f"No pods found with label app={DEPLOYMENT_NAME}")

    print()

    # Services
    result = subprocess.run(
        ["kubectl", "get", "svc", "-n", NAMESPACE, f"-l app={DEPLOYMENT_NAME}"],
        capture_output=True,
    )
    if result.returncode == 0:
        print(result.stdout.decode())
    else:
        print(f"No services found with label app={DEPLOYMENT_NAME}")

    print()

    # Ingress
    result = subprocess.run(
        ["kubectl", "get", "ingress", "-n", NAMESPACE, f"-l app={DEPLOYMENT_NAME}"],
        capture_output=True,
    )
    if result.returncode == 0:
        print(result.stdout.decode())
    else:
        print(f"No ingress found with label app={DEPLOYMENT_NAME}")

    return 0


def logs() -> int:
    """Get logs from the dev container."""
    log_info("Fetching logs from dev container...")
    try:
        run_command([
            "kubectl",
            "logs",
            "-n",
            NAMESPACE,
            f"-l app={DEPLOYMENT_NAME}",
            "--all-containers=true",
            "--follow",
        ])
        return 0
    except subprocess.CalledProcessError:
        return 1


def exec_cmd() -> int:
    """Execute commands in the dev container."""
    log_info("Connecting to dev container...")

    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "pods",
                "-n",
                NAMESPACE,
                f"-l app={DEPLOYMENT_NAME}",
                "-o",
                "jsonpath={.items[0].metadata.name}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        pod = result.stdout.strip()
        if not pod:
            log_error(f"No pod found for deployment {DEPLOYMENT_NAME}")
            return 1

        run_command(["kubectl", "exec", "-n", NAMESPACE, "-it", pod, "--", "bash"])
        return 0
    except subprocess.CalledProcessError:
        return 1


def port_forward() -> int:
    """Port forward to dev environment."""
    log_info("Setting up port forwarding...")

    try:
        result = subprocess.run(
            [
                "kubectl",
                "get",
                "pods",
                "-n",
                NAMESPACE,
                f"-l app={DEPLOYMENT_NAME}",
                "-o",
                "jsonpath={.items[0].metadata.name}",
            ],
            capture_output=True,
            text=True,
            check=True,
        )

        pod = result.stdout.strip()
        if not pod:
            log_error(f"No pod found for deployment {DEPLOYMENT_NAME}")
            return 1

        log_info("Forwarding ports 8080, 8000, 3000...")
        run_command([
            "kubectl",
            "port-forward",
            "-n",
            NAMESPACE,
            pod,
            "8080:8080",
            "8000:8000",
            "3000:3000",
        ])
        return 0
    except subprocess.CalledProcessError:
        return 1


def cleanup() -> int:
    """Remove the dev environment."""
    log_warning("Removing dev environment...")

    deployment_yaml = Path(".devcontainer/dev-deployment.yaml")
    if deployment_yaml.exists():
        subprocess.run(
            ["kubectl", "delete", "-f", str(deployment_yaml), "--ignore-not-found=true"],
            capture_output=True,
        )

    subprocess.run(
        [
            "kubectl",
            "delete",
            "secret",
            "kube-config",
            "ssh-keys",
            "git-config",
            "-n",
            NAMESPACE,
            "--ignore-not-found=true",
        ],
        capture_output=True,
    )

    log_success("Dev environment removed")
    return 0


def run_all() -> int:
    """Run build, secrets, and deploy in sequence."""
    if not check_kubectl() or not check_directory():
        return 1

    skip_push = os.environ.get("SKIP_PUSH", "false").lower() == "true"

    if build_image(skip_push) != 0:
        return 1
    if create_namespace() != 0:
        return 1
    if create_secrets() != 0:
        return 1
    if deploy() != 0:
        return 1

    return 0


def main() -> int:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Charon Dev Container Manager (Kali Linux)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Quick deploy
  %(prog)s all

  # Step by step
  %(prog)s build && %(prog)s secrets && %(prog)s deploy

  # Access the container
  %(prog)s exec

  # Check status
  %(prog)s status

Environment Variables:
  DOCKER_REGISTRY  Docker registry to push images (default: your-registry)
  SKIP_PUSH        Skip pushing image to registry (default: false)
        """,
    )

    parser.add_argument(
        "command",
        choices=[
            "build",
            "namespace",
            "secrets",
            "deploy",
            "status",
            "logs",
            "exec",
            "port-forward",
            "pf",
            "cleanup",
            "all",
            "help",
        ],
        help="Command to execute",
    )

    args = parser.parse_args()

    if args.command == "help":
        parser.print_help()
        return 0

    # Commands that need kubectl and directory check
    needs_kubectl = [
        "build",
        "namespace",
        "secrets",
        "deploy",
        "status",
        "logs",
        "exec",
        "port-forward",
        "pf",
        "cleanup",
        "all",
    ]

    if args.command in needs_kubectl:
        if not check_kubectl():
            return 1

    needs_directory = ["build", "deploy", "all"]
    if args.command in needs_directory:
        if not check_directory():
            return 1

    # Execute command
    commands = {
        "build": lambda: build_image(os.environ.get("SKIP_PUSH", "false").lower() == "true"),
        "namespace": create_namespace,
        "secrets": lambda: (create_namespace() or create_secrets()),
        "deploy": deploy,
        "status": status,
        "logs": logs,
        "exec": exec_cmd,
        "port-forward": port_forward,
        "pf": port_forward,
        "cleanup": cleanup,
        "all": run_all,
    }

    return commands[args.command]()


if __name__ == "__main__":
    sys.exit(main())
