#!/bin/bash
set -e

# Multiple database initialization script for PostgreSQL container
echo "Initializing multiple databases: $POSTGRES_MULTIPLE_DATABASES"

if [ -n "$POSTGRES_MULTIPLE_DATABASES" ]; then
    for db in $(echo $POSTGRES_MULTIPLE_DATABASES | tr ',' ' '); do
        echo "Creating database: $db"
        psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
            CREATE DATABASE $db;
EOSQL
    done
    echo "Multiple databases initialized successfully."
fi
