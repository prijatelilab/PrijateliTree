default: build start create_db

.PHONY: build
build:
	poetry export --without-hashes --format=requirements.txt > requirements.txt
	docker-compose build

.PHONY: start
start: build
	docker-compose up -d

.PHONY: create_db
create_db: start
	docker-compose exec web alembic -c ./prijateli_tree/migrations/alembic.ini upgrade head

.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: run
run:
	uvicorn prijateli_tree.app.main:app --reload --port 8000 --host 0.0.0.0

.PHONY: stop
stop:
	docker-compose stop

.PHONY: clean
clean: stop ## Remove all containers
	docker-compose rm -f

.PHONY: clean_all
clean_all: clean stop ## Wipe database
	docker-compose down -v
