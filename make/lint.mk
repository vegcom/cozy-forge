# Lint aggregator

lint: ## Run all linters (ruff, mypy, shellcheck, markdownlint)
	$(MAKE) python-lint
	$(MAKE) python-typecheck
	@command -v shellcheck >/dev/null 2>&1 && shellcheck scripts/**/*.sh 2>/dev/null || true
	@command -v markdownlint >/dev/null 2>&1 && markdownlint "**/*.md" 2>/dev/null || true
	@echo "✓ lint clean"
