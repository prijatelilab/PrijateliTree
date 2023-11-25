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
	@until docker-compose exec postgres psql -h localhost -U postgres -c '\l' postgres &>/dev/null; do \
		echo "Postgres is unavailable - sleeping..."; \
		sleep 1; \
	done
	@echo "Postgres is up"
	docker-compose run --rm web alembic --config=./prijateli_tree/migrations/alembic.ini upgrade head

.PHONY: update_db
update_db:
	docker-compose run --rm web alembic --config=./prijateli_tree/migrations/alembic.ini upgrade head

.PHONY: lint
lint:
	pre-commit run --all-files

.PHONY: test
test:
	pytest -vs ./prijateli_tree/tests/

.PHONY: stop
stop:
	docker-compose stop

.PHONY: clean
clean: stop ## Remove all containers
	docker-compose rm -f

.PHONY: clean_all
clean_all: clean stop ## Wipe database link
	docker-compose down -v
