# Cleanup helpers

clean: ## Remove build artifacts and cache dirs
	find . -type d -name __pycache__  -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache   -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache   -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ *.egg-info
	@echo "✓ clean"
