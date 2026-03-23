# Require variable helper
require-%:
		@if [ -z "$(${*})" ]; then \
				echo "Error: missing required argument '$*'"; \
				echo "Usage: make $*=<value> <target>"; \
				exit 1; \
		fi

# Include all sub-makefiles FIRST
include make/*.mk

# Default goal
.DEFAULT_GOAL := help

help: ## Show help
		@echo "Available targets:"
		@grep -E '^[a-zA-Z0-9_-]+:.*?##' $(MAKEFILE_LIST) | \
				awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}'


# Environment
## If direnv exists, allow it
ifneq ($(shell which direnv 2>/dev/null),)
DIR_ENV_ALLOWED := $(shell direnv allow .)
endif
## Choose shell
ifeq ($(shell test -x /bin/zsh && echo yes),yes)
SHELL := /bin/zsh
else
SHELL := /bin/bash
endif
