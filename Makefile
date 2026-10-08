.PHONY: help setup check lint test test-compat sync-agents check-agents

PRE_COMMIT := uvx pre-commit@4.3.0
# Tests run through uv so they do not depend on a local Pipenv environment.
UV_RUN := uv run --no-project --with pytest --with pytest-cov

help: ## List targets
	@grep -E '^[a-z-]+:.*## ' $(MAKEFILE_LIST) | awk -F':.*## ' '{printf "  %-12s %s\n", $$1, $$2}'

setup: ## Install the git hooks (pre-commit + commit-msg); needs uv
	$(PRE_COMMIT) install --install-hooks

check: lint test test-compat ## Everything to pass before finishing: hooks, then tests on 3.14 and 3.10

lint: ## Every hook in .pre-commit-config.yaml over the whole repo
	$(PRE_COMMIT) run --all-files --show-diff-on-failure

test: ## Tests with coverage on Python 3.14
	$(UV_RUN) --python 3.14 python -m pytest -q --cov=src --cov-report=term-missing

test-compat: ## Tests on Python 3.10, the oldest Python the action supports
	$(UV_RUN) --python 3.10 python -m pytest -q

sync-agents: ## Regenerate agent pointers from .agents/
	python3 tooling/sync_agents.py

check-agents: ## Fail if agent pointers drifted from .agents/
	python3 tooling/sync_agents.py --check
