# Kali Linux Dev Container for {{ cookiecutter.project_slug }} Infrastructure
FROM kalilinux/kali-rolling:latest

# Avoid interactive prompts during package installation
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/local/bin:$PATH"

# Update and install essential Kali packages
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    # Base development tools
    build-essential \
    git \
    curl \
    wget \
    unzip \
    ca-certificates \
    gnupg \
    lsb-release \
    software-properties-common \
    apt-transport-https \
    # Kali essentials
    kali-linux-headless \
    # Network tools
    dnsutils \
    net-tools \
    netcat-traditional \
    nmap \
    tcpdump \
    # Security tools
    openssl \
    openssh-client \
    # Utilities
    jq \
    yq \
    vim \
    nano \
    htop \
    tree \
    tmux \
    screen \
    zip \
    # Python development
    python3 \
    python3-pip \
    python3-venv \
    python3-dev \
    # Shell checking
    shellcheck \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install kubectl
RUN curl -LO "https://dl.k8s.io/release/$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl" \
    && chmod +x kubectl \
    && mv kubectl /usr/local/bin/kubectl

# Install Helm
RUN curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash

# Install Terraform
RUN wget -O- https://apt.releases.hashicorp.com/gpg | gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/hashicorp.list \
    && apt-get update \
    && apt-get install -y terraform \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install TFLint
RUN curl -s https://raw.githubusercontent.com/terraform-linters/tflint/master/install_linux.sh | bash

# Install Terragrunt
RUN TERRAGRUNT_VERSION=$(curl -s https://api.github.com/repos/gruntwork-io/terragrunt/releases/latest | grep -oP '"tag_name": "\K(.*)(?=")') \
    && wget -O /usr/local/bin/terragrunt "https://github.com/gruntwork-io/terragrunt/releases/download/${TERRAGRUNT_VERSION}/terragrunt_linux_amd64" \
    && chmod +x /usr/local/bin/terragrunt

# Install Docker CLI
RUN curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/debian bullseye stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    && apt-get update \
    && apt-get install -y docker-ce-cli docker-compose-plugin \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Node.js LTS and npm
RUN curl -fsSL https://deb.nodesource.com/setup_lts.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g yarn prettier eslint markdownlint-cli \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install yamllint and yamlfmt
RUN pip3 install --no-cache-dir yamllint \
    && wget -O /usr/local/bin/yamlfmt "https://github.com/google/yamlfmt/releases/latest/download/yamlfmt_$(uname -s)_$(uname -m)" \
    && chmod +x /usr/local/bin/yamlfmt

# Install Python development and infrastructure tools
RUN pip3 install --no-cache-dir \
    # Code quality tools
    ruff \
    black \
    flake8 \
    flake8-bugbear \
    flake8-comprehensions \
    flake8-pyproject \
    mypy \
    pyupgrade \
    # Testing
    pytest \
    pytest-cov \
    pytest-asyncio \
    # Pre-commit and git
    pre-commit \
    gitlint \
    # Infrastructure tools
    ansible \
    ansible-lint \
    checkov \
    # Cloud and API libraries
    requests \
    boto3 \
    kubernetes \
    pyyaml \
    jinja2 \
    python-dotenv \
    # Type stubs
    types-requests \
    types-python-dateutil

# Create non-root user
RUN useradd -m -s /bin/bash -u 1000 vscode \
    && usermod -aG sudo vscode \
    && echo "vscode ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/vscode \
    && chmod 0440 /etc/sudoers.d/vscode

# Set up workspace and mount points
RUN mkdir -p /workspaces/{{ cookiecutter.project_slug }} \
    /mnt/host-kube \
    /mnt/host-ssh \
    && chown -R vscode:vscode /workspaces/{{ cookiecutter.project_slug }}

# Copy Python scripts
COPY --chown=vscode:vscode .devcontainer/setup_mounts.py /usr/local/bin/setup_mounts.py
COPY --chown=vscode:vscode .devcontainer/startup.py /usr/local/bin/startup.py
COPY --chown=vscode:vscode .devcontainer/deploy_dev.py /usr/local/bin/deploy_dev.py
RUN chmod +x /usr/local/bin/setup_mounts.py \
    /usr/local/bin/startup.py \
    /usr/local/bin/deploy_dev.py

# Switch to vscode user
USER vscode
WORKDIR /workspaces/{{ cookiecutter.project_slug }}

# Set up git configuration
RUN git config --global init.defaultBranch main \
    && git config --global pull.rebase false

# Create Python virtual environment
RUN python3 -m venv /home/vscode/.venv \
    && echo 'source /home/vscode/.venv/bin/activate' >> /home/vscode/.bashrc

# Set up convenience aliases
RUN echo 'alias k="kubectl"' >> /home/vscode/.bashrc \
    && echo 'alias tf="terraform"' >> /home/vscode/.bashrc \
    && echo 'alias tg="terragrunt"' >> /home/vscode/.bashrc \
    && echo 'alias ll="ls -la"' >> /home/vscode/.bashrc \
    && echo 'alias la="ls -A"' >> /home/vscode/.bashrc \
    && echo 'alias l="ls -CF"' >> /home/vscode/.bashrc \
    && echo 'alias ..="cd .."' >> /home/vscode/.bashrc \
    && echo 'alias ...="cd ../.."' >> /home/vscode/.bashrc \
    && echo 'alias gst="git status"' >> /home/vscode/.bashrc \
    && echo 'alias gd="git diff"' >> /home/vscode/.bashrc \
    && echo 'alias gco="git checkout"' >> /home/vscode/.bashrc \
    && echo 'alias gcm="git commit -m"' >> /home/vscode/.bashrc

# Set environment variables
ENV KUBECONFIG="/home/vscode/.kube/config"
ENV VIRTUAL_ENV="/home/vscode/.venv"
ENV PATH="/home/vscode/.venv/bin:$PATH"

# Default command
CMD ["/bin/bash"]
