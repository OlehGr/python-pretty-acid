default: lint

lint:
	uv run -m ruff check --fix
	uv run -m ty check
