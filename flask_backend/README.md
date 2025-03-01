# Rent Prediction Backend

This is the backend for the Rent Prediction application. It provides both a REST API using Flask and a gRPC service.

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Generate Python code from Proto files:
   ```bash
   python generate_proto.py
   ```

3. Start the Flask server:
   ```bash
   python main.py
   ```

4. Start the gRPC server:
   ```bash
   python grpc_server.py
   ```

## API Endpoints

### REST API (Flask)

- **POST /predict**
  - Request body:
    ```json
    {
      "latitude": 51.5074,
      "longitude": -0.1278,
      "min_rent": 500,
      "max_rent": 1500
    }
    ```
  - Response:
    ```json
    {
      "district": "SW1",
      "predictions": {
        "SW1": 1500,
        "SW2": 1400
      },
      "location": {
        "latitude": 51.5074,
        "longitude": -0.1278
      }
    }
    ```

### gRPC Service

The gRPC service is defined in the proto file at `proto/rent_prediction.proto`. It provides the following RPC:

- **PredictRent**
  - Request:
    - `work_location`: Location (latitude, longitude)
    - `commute_time_minutes`: int32
    - `commute_type`: string ("walk", "drive", or "public")
    - `rent_option`: int32 (1, 2, or 3)
  - Response:
    - `predictions`: List of RentPrediction objects
    - `error_message`: string (if an error occurred)

## Docker

You can run the backend using Docker:

```bash
docker build -t rent-prediction-backend .
docker run -p 5000:5000 -p 5001:5001 rent-prediction-backend
```

Or using Docker Compose from the root directory:

```bash
docker-compose up
```
