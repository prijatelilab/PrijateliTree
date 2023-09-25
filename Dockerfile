# pull the official docker image
FROM python:3.11.1-slim

# set work directory
WORKDIR /app

ENV PYTHONPATH=${PYTHONPATH}:${PWD} \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

RUN apt-get update \
    && apt-get -y install libpq-dev gcc

# install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

ENV SQLALCHEMY_DATABASE_URI postgresql://prijateli:terriblepassword@postgres/prijateli_tree
