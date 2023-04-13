.PHONY: lint
lint:
	black .
	isort .

.PHONY: test
test:
	pytest -vv