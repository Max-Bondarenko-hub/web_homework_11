#To start/stop containers + migrate

docker-compose up -d
alembic revision --autogenerate -m 'Init'
alembic upgrade head
docker-compose stop

#Run unittests
python -m unittest discover tests

#Start server
uvicorn main:app --host 0.0.0.0 --port 8000