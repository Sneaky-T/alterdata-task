#!/bin/bash

echo "Waiting for database to be ready..."
while ! pg_isready -h db -p 5432 -U admin -d transactions_db; do
    sleep 2
done
echo "Database is ready!"

echo "Waiting for test database to be ready..."
while ! pg_isready -h test_db -p 5432 -U admin -d transactions_test_db; do
    sleep 2
done
echo "Test database is ready!"

echo "Starting FastAPI application..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 