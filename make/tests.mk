# Test helpers

# Run tests
test: ## Run Python tests
		pytest -q

# Run tests with coverage
test-coverage: ## Run tests with coverage report
		pytest --cov=src --cov-report=term-missing
