# Python helpers
PYTHON := python
PIP := pip

# Install project in editable mode
python-install: ## Install project in editable mode
		$(PYTHON) -m pip install -e .

# Run tests
python-test: ## Run Python tests
		$(PYTHON) -m pytest -q

# Format code
python-format: ## Format Python code with black
		$(PYTHON) -m black src tests

# Lint code
python-lint: ## Lint Python code with ruff
		$(PYTHON) -m ruff check src tests

# Fix lint issues
python-lint-fix: ## Auto-fix lint issues with ruff
		$(PYTHON) -m ruff check --fix src tests

# Type check
python-typecheck: ## Run mypy type checking
		$(PYTHON) -m mypy src
