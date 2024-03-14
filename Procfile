web: uvicorn prijateli_tree.app.main:app --workers 20 --host=0.0.0.0 --port=${PORT:-5000}
release: alembic --config=./prijateli_tree/migrations/alembic.ini upgrade head
