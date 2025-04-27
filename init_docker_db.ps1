# PowerShell script to initialize and seed the database in Docker

Write-Host "========================================" -ForegroundColor Green
Write-Host "Initializing and seeding the database..." -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green

# Check if docker-compose is running
$dockerRunning = docker-compose ps | Select-String "Up"
if (-not $dockerRunning) {
    Write-Host "Error: Docker Compose services are not running." -ForegroundColor Red
    Write-Host "Please start the services first with: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Option 1: Initialize using SQL script
Write-Host "1. Initializing database with SQL script..." -ForegroundColor Cyan
docker-compose exec db psql -U postgres -f /docker-entrypoint-initdb.d/init_db.sql

# Option 2: Seed the database with sample data
Write-Host "2. Seeding database with sample data..." -ForegroundColor Cyan
docker-compose exec api python scripts/seed_db.py

Write-Host "========================================" -ForegroundColor Green
Write-Host "Database initialization completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green 