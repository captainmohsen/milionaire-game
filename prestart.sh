#! /usr/bin/env bash
# install packages
# if [ $INSTALL_DEV == 'true' ]; then poetry install --no-root; else poetry install --no-root --no-dev; fi
# Let the DB start
python /app/app/backend_pre_start.py

# Run migrations
alembic upgrade heads

# Create initial data in DB
python /app/app/initial_data.py
