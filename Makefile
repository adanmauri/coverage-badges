.PHONY: help setup check lint test test-compat sync-agents check-agents

PRE_COMMIT := uvx pre-commit@4.3.0

help: ## List targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

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

sync-agents: ## Regenerate agent pointers from .agents/
	uv run --no-project tooling/sync_agents.py

check-agents: ## Fail if agent pointers drifted from .agents/
	uv run --no-project tooling/sync_agents.py --check
