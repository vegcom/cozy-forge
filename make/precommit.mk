# Run pre-commit hooks
precommit: ## Run all pre-commit hooks
		pre-commit run --all-files

# Install pre-commit hooks
precommit-install: ## Install pre-commit hooks into .git/hooks
		pre-commit install
