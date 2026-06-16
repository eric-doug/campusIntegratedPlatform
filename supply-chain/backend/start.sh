#!/bin/bash
set -e

echo "Starting Supply Chain Platform Backend..."

# Install shared module
if [ -d "/shared" ]; then
    pip install -e /shared 2>/dev/null || echo "Shared module already installed."
fi

# Wait for database
until python -c "import psycopg2; psycopg2.connect(host='${POSTGRES_HOST:-postgres}', port='${POSTGRES_PORT:-5432}', user='${POSTGRES_USER:-campus}', password='${POSTGRES_PASSWORD:-campus_dev_2026}', dbname='${POSTGRES_DB:-supply_chain}')" 2>/dev/null; do
    echo "Waiting for PostgreSQL..."
    sleep 2
done

echo "Database is ready."

# Start the application
if [ "${FLASK_ENV}" = "production" ]; then
    gunicorn -w 4 -b 0.0.0.0:5000 run:app
else
    python run.py
fi
