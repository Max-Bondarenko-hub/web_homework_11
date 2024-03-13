#To start/stop containers + migrate

docker-compose up -d
alembic revision --autogenerate -m 'Init'
alembic upgrade head
docker-compose stop