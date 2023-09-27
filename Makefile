#.PHONY: build
#build: ## Build containers
#	poetry export --without-hashes --format=requirements.txt > requirements.txt
#	docker-compose build

.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: run
run:
	uvicorn prijateli_tree.app.main:app --reload --port 8000 --host 0.0.0.0
