# Conda helpers

PRUNE :=
ARGS :=


conda-activate: ## Activate Conda environment
		conda activate $(_CONDA_ENV_NAME)

conda-deactivate: ## Deactivate Conda environment
		conda deactivate

conda-update: ## Activate Conda environment
ifdef PRUNE
ARGS += --prune
endif
		conda env update --file environment.yml $(ARGS)
