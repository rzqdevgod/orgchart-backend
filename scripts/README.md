# Database Setup and Seeding Scripts

This directory contains scripts for setting up and seeding the database for the OrgChat application.

## Available Scripts

1. `db_setup.py` - Creates the PostgreSQL database if it doesn't exist
2. `seed_db.py` - Seeds the database with sample organization charts and employees
3. `setup_and_seed.py` - Runs both scripts in sequence for a complete setup
4. `init_db.sql` - SQL script for database creation and schema definition
5. `run_sql_init.py` - Python script to run the SQL initialization

## Usage

### Prerequisites

Make sure you have installed all required dependencies:

```
pip install -r ../requirements.txt
```

For the SQL initialization script, you also need:
- PostgreSQL command-line tools (`psql`) installed and available in your PATH

### Environment Variables

The scripts use the following environment variables:

- `DATABASE_URL`: The PostgreSQL connection string (default: `postgresql://postgres:postgres@localhost:5432/orgchart`)
- `NUM_ORG_CHARTS`: Number of organization charts to create (default: 100)

You can set these in a `.env` file in the project root or pass them as environment variables.

### Running the Scripts

#### Complete Setup

For a complete setup (create database and seed):

```bash
python setup_and_seed.py
```

#### SQL Initialization

To initialize the database using raw SQL (alternative method):

```bash
python ../setup_database.py --sql-init
```

This will create the database and tables using the SQL script, which is useful for direct database setup.

#### Database Creation Only

To only create the database:

```bash
python db_setup.py
```

#### Database Seeding Only

To only seed the database:

```bash
python seed_db.py [number_of_org_charts]
```

You can optionally specify the number of organization charts to create as a command-line argument.

### Examples

```bash
# Create 50 organization charts
python seed_db.py 50

# Create database and 200 organization charts
NUM_ORG_CHARTS=200 python setup_and_seed.py

# Initialize with SQL and seed 50 organization charts
NUM_ORG_CHARTS=50 python ../setup_database.py --sql-init
``` 