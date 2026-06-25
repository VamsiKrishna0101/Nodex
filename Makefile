test:
	pytest

lint:
	ruff check src tests examples

format:
	ruff format src tests examples

publish:
	hatch build
