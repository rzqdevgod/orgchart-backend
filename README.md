# Org Chart Service

A FastAPI-based service for managing organization charts with hierarchical operations and multi-tenant storage.

## Features

- CRUD operations for org charts and employees
- Hierarchical operations with CEO protection
- Multi-tenant storage with proper isolation
- Containerized deployment with Docker and PostgreSQL
- Performance optimized for 10,000+ org charts

## Quick Start

### Option 1: Using Docker (Recommended)

1. Clone the repository:
```bash
git clone <repository-url>
cd orgchat-backend
```

2. Build and start the services:
```bash
# start the database contianer
docker-compose up -d db

# Run SQL script directly on the database container
docker-compose exec db psql -U postgres -f /docker-entrypoint-initdb.d/init_db.sql


# Start the API service in detached mode
docker-compose up -d api

# Initialize the database schema and seed data using the API container
docker-compose exec api python setup_database.py --sql-init

# Rebuild all services and start them in interactive mode (shows logs in terminal)
docker-compose up --build
```


The API will be available at `http://localhost:8000`

### Option 2: Local Development Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd orgchat-backend
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/MacOS
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL:
   - Install PostgreSQL 14 or later
   - Create a database named 'orgchart'
   - Create a user with password (or use default postgres user)

5. Set environment variables:
```bash

cp .env.example .env


6. Run the server:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## Database Initialization

### With Docker:

#### Option 1: Use the convenience script (recommended)
```bash
# For Linux/macOS:
./init_docker_db.sh

# For Windows:
.\init_docker_db.ps1
```

#### Option 2: Manual commands
```bash

# start the database contianer
docker-compose up -d db -d api

# Run SQL script directly on the database container
docker-compose exec db psql -U postgres -f /docker-entrypoint-initdb.d/init_db.sql
```

# Use SQL initialization (requires psql in the container)
docker-compose exec api python setup_database.py --sql-init

### Without Docker:
Use the database setup script to create and seed the database:

```bash
# Full setup: Create database and seed with sample data
python setup_database.py

# Only create the database
python setup_database.py --setup-only

# Only seed the database
python setup_database.py --seed-only

# Create a specific number of organization charts
python setup_database.py --num-orgs 50

# Initialize database using SQL script (requires psql)
python setup_database.py --sql-init
```

See the [`scripts/README.md`](scripts/README.md) for more details on database setup options.

## API Endpoints

### Org Charts
- `POST /orgcharts` - Create a new org chart
- `GET /orgcharts` - List all org charts

### Employees
- `POST /orgcharts/{org_id}/employees` - Create an employee in an org
- `GET /orgcharts/{org_id}/employees` - List employees in an org
- `DELETE /orgcharts/{org_id}/employees/{employee_id}` - Delete an employee
- `PUT /orgcharts/{org_id}/employees/{employee_id}/promote` - Promote an employee to CEO

## Hierarchy Logic

The service implements a self-referencing hierarchy where:
- Each employee (except CEO) has a manager
- The CEO has no manager (manager_id is NULL)
- Deleting a non-CEO employee automatically re-parents their reports
- CEO cannot be deleted directly (must be replaced via promote endpoint)

## Performance Optimization

The service is optimized for performance with:
- Indexes on foreign keys (org_id, manager_id)
- Efficient query patterns for hierarchy operations
- Batch operations for seeding data

## Environment Configuration

The service uses environment variables for configuration:

- Development: Uses default values in docker-compose.yml
- Production: Should use secure environment variables or secrets management

## Time Log

- API Logic & Models: 45 minutes
- Database Setup & Migrations: 15 minutes
- Containerization: 15 minutes
- Testing & Performance Optimization: 30 minutes
- Documentation: 15 minutes
- Total: ~2 hours

## Potential Enhancements

1. Authentication & Authorization
2. Caching layer for frequently accessed data
3. GraphQL interface for complex queries
4. WebSocket support for real-time updates
5. Advanced analytics and reporting