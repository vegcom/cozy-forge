# Dev setup helpers

# One-shot setup for a freshly cloned repo
dev: ## Set up dev environment (conda + hooks + install)
	$(MAKE) conda-create || true
	$(MAKE) precommit-install
	$(MAKE) python-install
	@echo "✓ dev environment ready — run 'make test' to verify"

# Sanity check — verify tooling is present
doctor: ## Check dev dependencies are installed
	@echo "Checking dev dependencies..."
	@command -v conda   >/dev/null 2>&1 && echo "  ✓ conda"    || echo "  ✗ conda (required)"
	@command -v python  >/dev/null 2>&1 && echo "  ✓ python"   || echo "  ✗ python (required)"
	@command -v pytest  >/dev/null 2>&1 && echo "  ✓ pytest"   || echo "  ✗ pytest (run: make python-install)"
	@command -v ruff    >/dev/null 2>&1 && echo "  ✓ ruff"     || echo "  ✗ ruff (run: make python-install)"
	@command -v mypy    >/dev/null 2>&1 && echo "  ✓ mypy"     || echo "  ✗ mypy (run: make python-install)"
	@command -v direnv  >/dev/null 2>&1 && echo "  ✓ direnv"   || echo "  ✗ direnv (optional but recommended)"
	@command -v pre-commit >/dev/null 2>&1 && echo "  ✓ pre-commit" || echo "  ✗ pre-commit (run: make precommit-install)"
