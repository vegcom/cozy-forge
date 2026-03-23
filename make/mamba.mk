# Mamba helpers

mamba-create: ## Create the conda environment
		@echo "Mamba: Create environment"
		mamba env create -yf environment.yml

mamba-update: ## Update the conda environment
		@echo "Mamba: Update environment"
		mamba env update --prune -yf environment.yml

mamba-remove: ## Remove the active conda environment
		@echo "Mamba: Remove environment"
		mamba env remove -yn $(_CONDA_ENV_NAME)

mamba-recreate: ## Recreate the environment from scratch
		@echo "Mamba: Recreate environment"
		$(MAKE) mamba-remove
		$(MAKE) mamba-create
