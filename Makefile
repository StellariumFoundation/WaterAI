.PHONY: install-uv build

install-uv:
	@uv --version > /dev/null 2>&1 || (echo "uv not found, installing..." && pip install uv)
	@uv --version > /dev/null 2>&1 && echo "uv is already installed."

build: install-uv
	@if [ -d ".venv" ]; then \
		echo ".venv already exists."; \
	else \
		echo "Creating .venv..."; \
		uv venv .venv; \
	fi
	@uv pip sync --python .venv/bin/python requirements.txt
