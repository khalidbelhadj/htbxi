# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Generate the gRPC code
RUN python generate_proto.py

# Make ports available to the world outside this container
EXPOSE 5000 5001

# Create a script to run both servers
RUN echo '#!/bin/bash\npython main.py &\npython grpc_server.py' > /app/start.sh
RUN chmod +x /app/start.sh

# Run the servers when the container launches
CMD ["/app/start.sh"]
