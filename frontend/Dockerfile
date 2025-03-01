# Use the official Node.js image from the Docker Hub
FROM node:16-alpine

# Set the working directory in the container
WORKDIR /app

# Copy package.json and yarn.lock
COPY package.json yarn.lock ./

# Install dependencies
RUN yarn install

# Copy the rest of the application code
COPY . .

# Generate the gRPC code
RUN yarn generate-proto

# Build the application
RUN yarn build

# Expose port 3000
EXPOSE 3000

# Start the application
CMD ["yarn", "start"]