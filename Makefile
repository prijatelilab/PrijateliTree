default: build start create_db

.PHONY: build
build:
	poetry export --without-hashes --format=requirements.txt > requirements.txt
	docker-compose build

.PHONY: start
start:
	docker-compose up -d

.PHONY: create_db
create_db:
	docker-compose run web alembic --config=./prijateli_tree/migrations/alembic.ini revision --autogenerate
	docker-compose run web alembic --config=./prijateli_tree/migrations/alembic.ini upgrade head

.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: stop
stop:
	docker-compose stop

.PHONY: clean
clean: stop ## Remove all containers
	docker-compose rm -f

.PHONY: clean_all
clean_all: clean stop ## Wipe database
	docker-compose down -v
