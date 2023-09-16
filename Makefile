.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: run
run:
	uvicorn --app-dir=./prijateli_tree/app main:app --reload
