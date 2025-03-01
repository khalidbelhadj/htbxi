# build docker image
PORT=$(grep -Ei '^port\s*=' config/config.ini | cut -d'=' -f2 | tr -d ' ')
docker build --build-arg PORT=$PORT -t my-grpc-server .

# run docker container
docker run -d -p $PORT:$PORT my-grpc-server