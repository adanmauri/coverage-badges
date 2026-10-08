.PHONY: help setup check lint test test-compat sync-agents check-agents
.DEFAULT_GOAL := help

PRE_COMMIT := uvx pre-commit@4.3.0

##@ General

help: ## Show this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} \
		/^[a-zA-Z0-9_-]+:.*?##/ { printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2 } \
		/^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) }' $(MAKEFILE_LIST)

##@ Development

setup: ## Create the environment and install the git hooks (pre-commit + commit-msg); needs uv
	uv sync --locked
	$(PRE_COMMIT) install --install-hooks

check: lint test test-compat ## Everything to pass before finishing: hooks, then tests on 3.14 and 3.10

lint: ## Every hook in .pre-commit-config.yaml over the whole repo
	$(PRE_COMMIT) run --all-files --show-diff-on-failure

test: ## Tests with coverage on the development Python (.python-version)
	uv run pytest -q --cov=src --cov-report=term-missing

test-compat: ## Tests on Python 3.10, the oldest Python the action supports, in a throwaway env
	uv run --isolated --python 3.10 --no-default-groups --group test pytest -q

##@ Agents

sync-agents: ## Regenerate agent pointers from .agents/
	uv run --no-project tooling/sync_agents.py

check-agents: ## Fail if agent pointers drifted from .agents/
	uv run --no-project tooling/sync_agents.py --check
