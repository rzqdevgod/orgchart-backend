-- Create database (run this first)
CREATE DATABASE orgchart;

-- Connect to the database
\c orgchart;

-- Create tables
CREATE TABLE org_charts (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL
);

CREATE TABLE employees (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    org_id INTEGER NOT NULL REFERENCES org_charts(id) ON DELETE CASCADE,
    manager_id INTEGER REFERENCES employees(id) ON DELETE SET NULL
);

-- Create indexes for performance
CREATE INDEX ix_employees_org_id ON employees(org_id);
CREATE INDEX ix_employees_manager_id ON employees(manager_id);

-- Grant permissions (if needed)
-- GRANT ALL PRIVILEGES ON DATABASE orgchart TO postgres;
-- GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO postgres; 