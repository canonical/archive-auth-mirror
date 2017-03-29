CHARM_NAME = archive-auth-mirror
CHARM_SERIES = xenial
CHARM_OUTPUT = build/charm-output
RENDERED_CHARM_DIR = $(CHARM_OUTPUT)/$(CHARM_SERIES)/$(CHARM_NAME)
RENDERED_CHARM_URI = cs:~landscape/$(CHARM_NAME)


.PHONY: help
help: ## Print help about available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'

.PHONY: charm-build
charm-build:  ## Build the charm
	rm -rf $(CHARM_OUTPUT)
	charm build -s $(CHARM_SERIES) -o $(CHARM_OUTPUT)

.PHONY: charm-push
charm-push: charm-build ## Push the rendered charm to the charm store
	echo -n "commit-sha-1: "  > $(RENDERED_CHARM_DIR)/repo-info
	echo $(shell git rev-parse HEAD) >> $(RENDERED_CHARM_DIR)/repo-info
	charm push $(RENDERED_CHARM_DIR) $(RENDERED_CHARM_URI)

.DEFAULT_GOAL := help
