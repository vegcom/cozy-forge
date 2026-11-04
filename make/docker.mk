# Docker helpers

DOCKER := docker
CONTEXT := default
_FORCE_RECREATE := false
_MAX_LOG_LINES := 20
ARGS :=

define FILES
services/forge-service/compose.yml
endef

define CONTAINERS
forge-service
endef

_docker_log: 
	@echo '{"CONTEXT": "$(CONTEXT)", "FILES": "$(FILES)", "CONTAINERS": "$(CONTAINERS)"}'

CONTAINERS := $(foreach item,$(strip $(CONTAINERS)),"$(item)")
FILES := $(foreach item,$(strip $(FILES)),-f "$(item)")

# -------------------------------------------------------------------
# Managing docker image/container
# -------------------------------------------------------------------

# Build via docker compose plugin
docker-svc-build: ## Build docker container
	@$(MAKE) _docker_log CONTEXT=$(CONTEXT) FILES='$(FILES)' CONTAINERS='$(CONTAINERS)'
	@$(DOCKER) --context $(CONTEXT) compose $(FILES) build $(CONTAINERS) $(ARGS)

# Start svc via docker compose plugin
docker-svc-up: ## docker compose up
	@$(MAKE) _docker_log CONTEXT=$(CONTEXT) FILES='$(FILES)' CONTAINERS='$(CONTAINERS)'
	@$(DOCKER) --context $(CONTEXT) compose $(FILES) up $(CONTAINERS) $(ARGS)

# Build and start svc via compose plugin
docker-svc: ## docker compose build then up
	@$(MAKE) docker-svc-build CONTEXT=$(CONTEXT) FILES='$(FILES)' CONTAINERS='$(CONTAINERS)'
	@$(MAKE) docker-svc-up CONTEXT=$(CONTEXT) FILES='$(FILES)' CONTAINERS='$(CONTAINERS)'

# -------------------------------------------------------------------
# Auditing docker container
# -------------------------------------------------------------------

# view svc logs via docker compose plugin
docker-svc-log: ## Init docker container
	@$(MAKE) _docker_log CONTEXT=$(CONTEXT) FILES='$(FILES)' CONTAINERS='$(CONTAINERS)'
	@$(DOCKER) --context $(CONTEXT) compose $(FILES) logs $(CONTAINERS) $(ARGS := --tail 20) 

# View config via docker compose plugin
docker-svc-config: ## View docker compose config
	@$(MAKE) _docker_log CONTEXT=$(CONTEXT) FILES='$(FILES)' CONTAINERS='$(CONTAINERS)'
	@$(DOCKER) --context $(CONTEXT) run -i --rm mikefarah/yq --colors <<(docker compose $(FILES) config)