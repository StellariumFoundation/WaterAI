.PHONY: build test

build:
	@echo "Ensuring .venv is created..."
	@uv venv .venv
	@echo "Syncing dependencies..."
	@uv pip sync requirements.txt --python .venv/bin/python

test:
	@echo "Activating virtual environment and running tests..."
	@. .venv/bin/activate && python -m unittest discover tests
