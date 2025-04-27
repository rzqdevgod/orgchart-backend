#!/usr/bin/env python
"""
Script to run the database initialization SQL script.
This script handles database creation and table setup.
"""

import os
import sys
import subprocess
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

def run_sql_script():
    """Run the SQL initialization script using psql."""
    try:
        # Get database connection details from environment
        database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/postgres")
        
        # Parse connection details from URL
        url_parts = database_url.split("://")[1].split("@")
        auth_parts = url_parts[0].split(":")
        conn_parts = url_parts[1].split("/")[0].split(":")
        
        username = auth_parts[0]
        password = auth_parts[1]
        host = conn_parts[0]
        port = conn_parts[1] if len(conn_parts) > 1 else "5432"
        
        # Set PGPASSWORD environment variable for psql
        os.environ["PGPASSWORD"] = password
        
        # Path to the SQL script
        sql_script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "init_db.sql")
        
        print(f"Running SQL initialization script from {sql_script_path}")
        
        # Run the psql command
        result = subprocess.run([
            "psql",
            "-h", host,
            "-p", port,
            "-U", username,
            "-f", sql_script_path
        ], check=False, capture_output=True, text=True)
        
        # Check for errors
        if result.returncode != 0:
            print("Error running SQL script:")
            print(result.stderr)
            return False
        
        print("SQL script output:")
        print(result.stdout)
        print("Database initialization completed successfully!")
        return True
        
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = run_sql_script()
    sys.exit(0 if success else 1) 