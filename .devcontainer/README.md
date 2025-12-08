# {{ cookiecutter.project_slug }} Kali Dev Container

A production-ready development container based on **Kali Linux** for infrastructure security and Kubernetes
development.

## Features

### Base Image

- **Kali Linux Rolling** - Latest security tools and packages
- All Kali headless tools pre-installed
- Network security tools (nmap, tcpdump, netcat)

### Development Tools

- **Kubernetes**: kubectl, Helm 3
- **Infrastructure as Code**: Terraform, TFLint, Terragrunt
- **Python 3**: Full development environment with venv
- **Node.js LTS**: npm, yarn, prettier, eslint
- **Docker**: Docker CLI with compose plugin

### Code Quality Tools

All pre-commit tools are pre-installed:

- **Python**: ruff, black, flake8, mypy, pyupgrade, pytest
- **Terraform**: terraform fmt, validate, docs, checkov
- **YAML**: yamllint, yamlfmt
- **Markdown**: markdownlint
- **Shell**: shellcheck
- **Git**: gitlint, GitHub CLI

### VS Code Extensions

Pre-configured with:

- Python (Pylance, Black, Ruff)
- Terraform (HashiCorp official)
- Kubernetes Tools
- Docker
- YAML, Markdown, Shell support
- GitHub Actions support

## Quick Start

### Option 1: VS Code Dev Containers (Recommended - Windows & Linux)

1. Install [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
2. Open the project in VS Code
3. Click "Reopen in Container" when prompted
4. Wait for the container to build (first time only)

The setup script (`setup_mounts.py`) automatically detects your OS and configures paths accordingly.

### Option 2: Docker Compose (Windows & Linux)

```bash
# Start the dev container
docker-compose -f .devcontainer/docker-compose.yml up -d

# Attach to the container
docker exec -it {{ cookiecutter.project_slug }}-dev bash

# Stop the container
docker-compose -f .devcontainer/docker-compose.yml down
```

### Option 3: Manual Docker Build (Advanced)

**Linux/Mac:**
```bash
# Build the image
docker build -f .devcontainer/Dockerfile -t {{ cookiecutter.project_slug }}-dev:latest .

# Run the container
docker run -it --rm \
  -v $(pwd):/workspaces/{{ cookiecutter.project_slug }} \
  -v ~/.kube:/mnt/host-kube:ro \
  -v ~/.ssh:/mnt/host-ssh:ro \
  -v ~/.gitconfig:/mnt/host-gitconfig:ro \
  --network=host \
  --cap-add=NET_ADMIN \
  --cap-add=NET_RAW \
  {{ cookiecutter.project_slug }}-dev:latest
```

**Windows (PowerShell):**
```powershell
# Build the image
docker build -f .devcontainer/Dockerfile -t {{ cookiecutter.project_slug }}-dev:latest .

# Run the container
docker run -it --rm `
  -v ${PWD}:/workspaces/{{ cookiecutter.project_slug }} `
  -v ${env:USERPROFILE}\.kube:/mnt/host-kube:ro `
  -v ${env:USERPROFILE}\.ssh:/mnt/host-ssh:ro `
  -v ${env:USERPROFILE}\.gitconfig:/mnt/host-gitconfig:ro `
  --network=host `
  --cap-add=NET_ADMIN `
  --cap-add=NET_RAW `
  {{ cookiecutter.project_slug }}-dev:latest
```

## Configuration

### Mounted Directories

The devcontainer automatically mounts from your host system:

- `~/.kube/config` - Kubernetes config (copied to container if exists)
- `~/.ssh/` - SSH keys (copied to container if exists)
- `~/.gitconfig` - Git configuration (copied if exists)
- `.env` - Environment variables (linked if exists in project root)
- `terraform/terraform.tfvars` - Terraform variables (linked if exists)

**Note**: All host mounts are read-only. Files are copied into the container on startup via the
`setup_mounts.py` Python script. This script automatically:

- Detects your operating system (Linux, Mac, Windows)
- Handles path differences between platforms
- Copies configuration files with proper permissions
- Provides helpful feedback if files are missing

If configuration files don't exist on your host, the container will use defaults or prompt you to
configure them manually.

### Environment Variables

```bash
KUBECONFIG=/home/vscode/.kube/config
VIRTUAL_ENV=/home/vscode/.venv
PATH=/home/vscode/.venv/bin:...
```

### Port Forwarding

Automatically forwards:

- `3000` - Web UI
- `8000` - vLLM API
- `8080` - API Server
- `8443` - HTTPS

## Post-Create Setup

The container automatically:

1. Activates Python virtual environment
2. Upgrades pip
3. Installs project dependencies from `pyproject.toml` (if available)
4. Installs pre-commit hooks
5. Displays ready message

## Development Workflow

### Initial Setup

```bash
# Initialize Terraform
cd terraform
terraform init

# Install pre-commit hooks (done automatically)
pre-commit install

# Verify installation
terraform version
python --version
kubectl version --client
```

### Running Pre-commit Checks

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run ruff --all-files
pre-commit run terraform_fmt --all-files
```

### Testing Python Code

```bash
# Activate venv (done automatically in terminal)
source ~/.venv/bin/activate

# Run tests
pytest

# Run with coverage
pytest --cov=scripts --cov-report=html
```

### Terraform Operations

```bash
# Format code
terraform fmt -recursive

# Validate configuration
terraform validate

# Plan changes
terraform plan

# Apply changes
terraform apply
```

## Kubernetes Deployment

Deploy the dev container to Kubernetes for remote development:

```bash
# Build and deploy everything
python3 .devcontainer/deploy_dev.py all

# Or step by step
python3 .devcontainer/deploy_dev.py build
python3 .devcontainer/deploy_dev.py secrets
python3 .devcontainer/deploy_dev.py deploy

# Check status
python3 .devcontainer/deploy_dev.py status

# Access the container
python3 .devcontainer/deploy_dev.py exec

# Port forward
python3 .devcontainer/deploy_dev.py port-forward

# Cleanup
python3 .devcontainer/deploy_dev.py cleanup

# Or use the installed command (if in container)
deploy_dev.py all
```

## Convenience Aliases

Pre-configured shell aliases:

```bash
k          # kubectl
tf         # terraform
tg         # terragrunt
ll         # ls -la
gst        # git status
gd         # git diff
gco        # git checkout
gcm        # git commit -m
```

## Troubleshooting

### Container Build Issues

```bash
# Clear Docker cache
docker builder prune -a

# Rebuild without cache
docker build --no-cache -f .devcontainer/Dockerfile -t {{ cookiecutter.project_slug }}-dev:latest .
```

### Kubeconfig Not Found

Ensure `~/.kube/config` exists on your host system:

```bash
# Verify kubeconfig
ls -la ~/.kube/config

# Test kubectl access
kubectl cluster-info
```

### Pre-commit Hooks Failing

```bash
# Update pre-commit
pre-commit autoupdate

# Clear cache and reinstall
pre-commit clean
pre-commit install --install-hooks
```

### Python Virtual Environment

```bash
# Recreate venv if corrupted
rm -rf ~/.venv
python3 -m venv ~/.venv
source ~/.venv/bin/activate
pip install --upgrade pip
```

## Security Features

### Kali Linux Tools

Access to penetration testing and security tools:

- Network scanning: nmap, tcpdump
- SSL/TLS testing: openssl
- Protocol analysis: netcat
- DNS utilities: dig, nslookup

### Container Capabilities

The container runs with:

- `NET_ADMIN` - For network operations
- `NET_RAW` - For raw socket access
- `--network=host` - Direct host network access

### Security Best Practices

- Non-root user (`vscode`) with sudo access
- SSH keys and kubeconfig mounted read-only
- Virtual environment for Python isolation
- Pre-commit hooks for security scanning (checkov)

## Customization

### Adding Python Packages

Edit `pyproject.toml`:

```toml
[project]
dependencies = [
    "your-package>=1.0.0",
]
```

Then rebuild or run:

```bash
pip install -e .
```

### Adding System Packages

Edit `.devcontainer/Dockerfile`:

```dockerfile
RUN apt-get update && apt-get install -y \
    your-package \
    && apt-get clean
```

### Adding VS Code Extensions

Edit `.devcontainer/devcontainer.json`:

```json
{
  "customizations": {
    "vscode": {
      "extensions": [
        "publisher.extension-name"
      ]
    }
  }
}
```

## Resources

- [Dev Containers Documentation](https://code.visualstudio.com/docs/devcontainers/containers)
- [Kali Linux Docs](https://www.kali.org/docs/)
- [Charon Project README](../README.md)
- [CLAUDE.md](../CLAUDE.md) - AI assistant guidelines

## Support

For issues or questions:

1. Check the [main documentation](../docs/)
2. Review [CLAUDE.md](../CLAUDE.md) for development patterns
3. Open an issue on GitHub
