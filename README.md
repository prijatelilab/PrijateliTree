# Prijateli Tree
`PrijateliTree` is an oTree application used to play lab games and collect survey data.
The games are a means to provide insights into social learning, the economics of languages
and other human behaviors.

## Application Requirements
- Python 🐍 version >= v`3.11`
- Poetry package manager. If you need information on how to download poetry, check [here](https://python-poetry.org/docs/#installation).
- PostgreSQL v14.
  - For accessing the database your configuration should look roughly like this:
  <img src="misc/DBConfig.png" alt="Database Access Configuration" width="400px">

## Steps for Running the Application
1. Enter the `poetry shell` command from the base folder repository.
2. Run the command `make` from the base directory.
3. Access the application via the URL `localhost:8000`.

## Dev commands
- `make lint`: Runs the `pre-commit` processes and lints the repository.
- `make create_requirements`: Creates a `requirements.txt` file based off of the imported packages in the `pyproject.toml` file.
- `make build`: Builds the Docker images for the application and the database pass through.
- `make start`: Starts the Docker containers based on the images created in the `make build` step.
- `make create_db`: Runs the alembic scripts. This MUST be run before you run the `make start` command, or it will error.
- `make update_db`: Updates the DB to the latest Alembic version.
- `make stop`: Stops the running Docker containers.
- `make clean`: Removes all Docker containers.
- `make clean_all`: Removes the database link between the Docker containers and the self-hosted version of PostgreSQL.
- `make test`: Runs all the tests in the `prijateli_tree/tests` folder using a Dockerized version of SQLite.
- `make process_translations`: Runs `process_translations.py` -- ensure the latest excel file is in `/app/languages/` and adjust the filename in `constants` if necessary.

## General Debugging Notes
- If you are failing the `Format-and-Fail` GitHub Action, you must run `make lint` and make any changes it requests.
- If you have already run the `make` command, you cannot run it again UNLESS you delete all the tables in your hosted database.
  - This is because the command will attempt to run the Alembic scripts again which will error since all the tables already exist.

## Data Migrations
To run a data migration, you need to run the following steps:
1. Before you make any changes to the `database.py` file in the `app` directory, run the following command from your terminal:
`docker-compose run web alembic --config=./prijateli_tree/migrations/alembic.ini stamp head`
   - You can also use the command `make stamp`
2. Make your modifications to the `database.py` file in the `app` directory.
3. Run the following command from your terminal to produce your migration: `docker-compose run web alembic --config=./prijateli_tree/migrations/alembic.ini revision --autogenerate`
   - You can also use the command `make create_revision`
4. You should then see a file added to the `migrations/versions` folder. Modify that as is necessary as Alembic isn't guaranteed to make all the necessary changes.
5. Run the following command and your migration should be run on the database: `docker-compose run web alembic --config=./prijateli_tree/migrations/alembic.ini upgrade head`
   - You can also use the command `make upgrade_db`
