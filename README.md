#To start containers
docker run --name contacts -p 5432:5432 -e POSTGRES_PASSWORD=pass123 -d postgres
docker run --name my-redis -p 6379:6379 -d redis