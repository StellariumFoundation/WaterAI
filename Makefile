.PHONY: build

build:
	@echo "Ensuring .venv is created..."
	@uv venv .venv
	@echo "Syncing dependencies..."
	@uv pip sync requirements.txt
