#!/bin/bash
set -e

# Wait for PostgreSQL to be ready
until pg_isready -h "$DB_HOST" -U "$DB_USER"; do
  echo >&2 "Postgres is unavailable - sleeping"
  sleep 2
done

# Wait for LocalStack to be ready
until curl -s http://localstack:4566/ > /dev/null; do
  echo >&2 "LocalStack is unavailable - sleeping"
  sleep 2
done

# Run the main script
exec "$@"
