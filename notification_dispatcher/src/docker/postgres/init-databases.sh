#!/bin/bash
set -e

# Create application databases (postgres image runs scripts as POSTGRES_USER)
psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" <<-EOSQL
    SELECT 'CREATE DATABASE auth' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'auth')\gexec
    SELECT 'CREATE DATABASE market' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'market')\gexec
    SELECT 'CREATE DATABASE chat' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'chat')\gexec
    SELECT 'CREATE DATABASE admin' WHERE NOT EXISTS (SELECT FROM pg_database WHERE datname = 'admin')\gexec
EOSQL
