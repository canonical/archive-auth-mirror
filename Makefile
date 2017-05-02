CHARM_NAME = archive-auth-mirror
CHARM_SERIES = xenial
CHARM_OUTPUT = build/charm-output
RENDERED_CHARM_DIR = $(CHARM_OUTPUT)/$(CHARM_SERIES)/$(CHARM_NAME)
CHARM_URI = cs:~landscape/$(CHARM_NAME)


.PHONY: help
help: ## Print help about available targets
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}'


.PHONY: install-deps
install-deps: TEST_DEPS = tox
install-deps: TEST_DEPS += $(shell python3 -c 'import yaml; print(" ".join(yaml.load(open("layer.yaml"))["options"]["basic"]["packages"]))')
install-deps:  ## Install test dependency deb packages
	@sudo apt install $(TEST_DEPS)

.PHONY: charm-build
charm-build: REV_HASH = $(shell git rev-parse HEAD)
charm-build: export INTERFACE_PATH = interfaces
charm-build: ## Build the charm
	rm -rf $(CHARM_OUTPUT)
	charm build -s $(CHARM_SERIES) -o $(CHARM_OUTPUT)
	echo "commit-sha-1: $(REV_HASH)" > $(RENDERED_CHARM_DIR)/repo-info

.PHONY: charm-push
charm-push: charm-build ## Push the charm to the store and release it in the edge channel
	./release-charm $(RENDERED_CHARM_DIR) $(CHARM_URI)

.DEFAULT_GOAL := help
