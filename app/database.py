from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv

load_dotenv()

# Get database URL from environment or use a default
# Format should be postgresql://username:password@hostname:port/database
db_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/orgchart")

# Fix URL format if needed (handle potential format issues)
if "://" not in db_url:
    # If protocol missing, assume postgresql
    db_url = f"postgresql://{db_url}"

SQLALCHEMY_DATABASE_URL = db_url

# Create SQLAlchemy engine with connection pooling
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    pool_size=10,
    max_overflow=20
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close() 