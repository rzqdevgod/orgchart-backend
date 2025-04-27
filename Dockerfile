FROM python:3.11-slim

WORKDIR /app

# Install postgresql-client for SQL initialization
RUN apt-get update && apt-get install -y postgresql-client && apt-get clean

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make sure the SQL init script is copied to a location that can be mounted by the DB container
RUN mkdir -p /docker-entrypoint-initdb.d/
COPY scripts/init_db.sql /docker-entrypoint-initdb.d/

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"] 