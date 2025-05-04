docker-compose up -d db

docker-compose exec db psql -U postgres -f /docker-entrypoint-initdb.d/init_db.sql

docker-compose up -d api

docker-compose exec api python setup_database.py --sql-init

docker-compose up --build