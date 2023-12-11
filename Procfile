web: uvicorn -w 2 -k prijateli_tree.app.main:app
release: alembic --config=./prijateli_tree/migrations/alembic.ini upgrade head
