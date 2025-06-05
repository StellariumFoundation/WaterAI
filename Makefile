.PHONY: build test

build:
	@echo "Ensuring .venv is created..."
	@uv venv .venv
	@echo "Syncing dependencies..."
	@uv pip sync requirements.txt

test:
	@echo "Running tests..."
	@python -m unittest discover tests
