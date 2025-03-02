
# Rent Prediction Application

This project is a rent prediction application that helps users find rental properties based on their work location, commute preferences, and rent preferences. This innovative tool that assists people in making the best decisions for their specific situations; by analyzing cost of living and financial impacts across different areas. It utilizes a mixture of live and historical data, ranging from postcode-specific information to broader macroeconomic factors.

## Features

- Select work location on the map
- Set commute preferences (time and mode of transport)
- Set rent preferences
- View rent predictions on the map

## Technologies Used

- TypeScript
- React
- Mapbox GL
- Framer Motion
- React Query
- ProtoBuf

## Setup

1. Clone the repository:
    ```sh
    git clone <repository-url>
    cd htbxi
    ```

2. Install dependencies:
    ```sh
    npm install
    ```

3. Set up environment variables:
    Create a `.env` file in the root directory and add your Mapbox token:
    ```env
    NEXT_PUBLIC_MAPBOX_TOKEN=your_mapbox_token
    ```

4. Run the application:
    ```sh
    npm run dev
    ```

5. Open your browser and navigate to `http://localhost:3000`.

## Backend Setup

1. Ensure you have Python installed.
2. Navigate to the backend directory:
    ```sh
    cd backend
    ```

3. Install Python dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Run the backend server:
    ```sh
    uv run main.py
    ```

5. The backend server will be running on `http://127.0.0.1:5000`.


