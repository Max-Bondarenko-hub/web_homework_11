#To start container
docker run --name contacts -p 5432:5432 -e POSTGRES_PASSWORD=pass123 -d postgres
