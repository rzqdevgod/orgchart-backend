#!/bin/bash

# Script to initialize and seed the database in Docker

echo "========================================"
echo "Initializing and seeding the database..."
echo "========================================"

# Check if docker-compose is running
if ! docker-compose ps | grep -q "Up"; then
  echo "Error: Docker Compose services are not running."
  echo "Please start the services first with: docker-compose up -d"
  exit 1
fi

# Option 1: Initialize using SQL script
echo "1. Initializing database with SQL script..."
docker-compose exec db psql -U postgres -f /docker-entrypoint-initdb.d/init_db.sql

# Option 2: Seed the database with sample data
echo "2. Seeding database with sample data..."
docker-compose exec api python scripts/seed_db.py

echo "========================================"
echo "Database initialization completed!"
echo "========================================" 