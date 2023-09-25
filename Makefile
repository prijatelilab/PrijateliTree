default: build start create_db

.PHONY: build
build: ## Build containers
	poetry export --without-hashes --format=requirements.txt > requirements.txt
	docker-compose build

.PHONY: start
start: build ## Run containers
	docker-compose up -d

.PHONY: create_db
create_db: start
	@until docker-compose exec postgres psql -h localhost -d prijateli_tree -U prijateli -c '\l' postgres &>/dev/null; do \
		echo "Postgres is unavailable - sleeping..."; \
		sleep 1; \
	done
	@echo "Postgres is up"
	## Creating database
	docker-compose run --rm web alembic --config=./prijateli_tree/migrations/alembic.ini stamp head

.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: run
run:
	uvicorn --app-dir=./prijateli_tree/app main:app --reload

.PHONY: stop
stop:
	docker-compose stop

.PHONY: clean
clean: stop ## Remove all containers
	docker-compose rm -f

.PHONY: clean_all
clean_all: clean stop ## Wipe database
	docker-compose down -v
