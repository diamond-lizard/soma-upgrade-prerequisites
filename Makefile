.PHONY: help ruff ruff-fix mypy test

help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

ruff: ## Run ruff linter
	uv run ruff check src/ tests/

ruff-fix: ## Run ruff linter with auto-fix
	uv run ruff check --fix src/ tests/

mypy: ## Run mypy type checker
	uv run mypy src/

test: ruff mypy ## Run ruff, mypy, then pytest
	uv run pytest tests/
