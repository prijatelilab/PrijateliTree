# Prijateli Tree
`PrijateliTree` is an oTree application used to play lab games and collect survey data.
The games are a means to provide insights into social learning, the economics of languages and other human behaviors.

## Application Requirements
- Python 🐍 version >= v`3.11`
- Poetry package manager. If you need information on how to download poetry, check [here](https://python-poetry.org/docs/#installation).
- PostgreSQL v14.
  - For accessing the database your configuration should look roughly like this:
  ![Database Access Configuration](misc%2FScreenshot%202023-10-02%20at%204.41.36%20PM.png)

## Steps for Running the Application
1. Enter the `poetry shell` command from the base folder repository.
2. Run the command `make` from the base directory.
3. Access the application via the URL `localhost:8000`.

## Dev commands
`make lint`: Runs the `pre-commit` processes and lints the repository.

## Data Migrations
To run a data migration, you need to run the following steps:
1. Before you make any changes to the `database.py` file in the `models` directory, run the following command from your terminal:
`docker-compose run web alembic --config=./prijateli_tree/migrations/alembic.ini stamp head`
2. Make your modifications to the `database.py` file in the `models` directory.
3. Run the following command from your terminal to produce your migration: `docker-compose run web alembic --config=./prijateli_tree/migrations/alembic.ini revision --autogenerate`
4. You should then see a file added to the `migrations/versions` folder. Modify that as is necessary as Alembic isn't guaranteed to make all the necessary changes.
5. Run the following command and your migration should be run on the database: `docker-compose run web alembic --config=./prijateli_tree/migrations/alembic.ini upgrade head`
