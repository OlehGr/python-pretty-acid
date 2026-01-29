default: lint

lint:
	uv run ruff check --fix
	uv run -m mypy .
