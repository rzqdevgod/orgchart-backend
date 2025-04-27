import sys
import os
import psycopg2
from dotenv import load_dotenv

# Add the parent directory to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

load_dotenv()

# Parse the database URL
database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/orgchart")
params = {}

if "://" in database_url:
    # Handle URL format
    url_parts = database_url.split("://")[1].split("@")
    auth_parts = url_parts[0].split(":")
    conn_parts = url_parts[1].split("/")
    host_port = conn_parts[0].split(":")
    
    params["user"] = auth_parts[0]
    params["password"] = auth_parts[1]
    params["host"] = host_port[0]
    params["port"] = host_port[1] if len(host_port) > 1 else "5432"
    params["database"] = "postgres"  # Connect to default postgres db first
    target_db = conn_parts[1]
else:
    # If not properly formatted, use defaults
    params["user"] = "postgres"
    params["password"] = "postgres"
    params["host"] = "localhost"
    params["port"] = "5432"
    params["database"] = "postgres"  # Connect to default postgres db first
    target_db = "orgchart"

def create_database():
    # Connect to default postgres database
    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Check if database exists
    cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{target_db}'")
    exists = cur.fetchone()
    
    if not exists:
        print(f"Creating database: {target_db}")
        # Create database if it doesn't exist
        cur.execute(f"CREATE DATABASE {target_db}")
        print(f"Database {target_db} created successfully!")
    else:
        print(f"Database {target_db} already exists.")
    
    # Close connection
    cur.close()
    conn.close()

if __name__ == "__main__":
    create_database() 