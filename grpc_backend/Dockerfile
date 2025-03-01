FROM python:3.9-slim

WORKDIR /app
COPY . .

# install uv dependencies and set up uv for path
RUN pip install uv

# add dependencies
RUN uv add grpcio
RUN uv add grpcio-tools

# setup protobuf files
RUN uv run python -m grpc_tools.protoc \
    --proto_path=. \
    --python_out=. \
    --grpc_python_out=. \
    protos/example.proto

# use port from config.ini
EXPOSE ${PORT}

CMD ["uv", "sync", "&&", "run", "server.py"]