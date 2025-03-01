"use client";

import { LngLat } from "./types";
import { RentPredictionServiceClient } from "./proto/rent_prediction_grpc_web_pb";
import { PredictionRequest, Location, PredictionResponse } from "./proto/rent_prediction_pb";

// Define the types for our function parameters
type CommuteType = "walk" | "drive" | "public";
type RentOption = 1 | 2 | 3;

interface PredictRentParams {
  workLocation: LngLat;
  commuteTimeMinutes: number;
  commuteType: CommuteType;
  rentOption: RentOption;
}

interface RentPrediction {
  district: string;
  meanRent: number;
  medianRent: number;
  location: {
    latitude: number;
    longitude: number;
  };
}

/**
 * Makes a gRPC request to predict rent based on work location, commute preferences, and rent options
 * @param params The parameters for the rent prediction
 * @returns A promise that resolves to an array of rent predictions
 */
export async function predictRent(params: PredictRentParams): Promise<RentPrediction[]> {
  // Create a gRPC client
  const client = new RentPredictionServiceClient('http://localhost:5001');

  // Create a location message
  const location = new Location();
  location.setLatitude(params.workLocation.lat);
  location.setLongitude(params.workLocation.lng);

  // Create the request message
  const request = new PredictionRequest();
  request.setWorkLocation(location);
  request.setCommuteTimeMinutes(params.commuteTimeMinutes);
  request.setCommuteType(params.commuteType);
  request.setRentOption(params.rentOption);

  return new Promise((resolve, reject) => {
    client.predictRent(request, {}, (err, response) => {
      if (err) {
        console.error("Error predicting rent:", err);
        reject(err);
        return;
      }
      
      if (response.getErrorMessage()) {
        const error = new Error(response.getErrorMessage());
        console.error("Error predicting rent:", error);
        reject(error);
        return;
      }
      
      // Convert the response to our frontend type
      const predictions = response.getPredictionsList().map((prediction) => ({
        district: prediction.getDistrict(),
        meanRent: prediction.getMeanRent(),
        medianRent: prediction.getMedianRent(),
        location: {
          latitude: prediction.getLocation().getLatitude(),
          longitude: prediction.getLocation().getLongitude(),
        },
      }));
      
      resolve(predictions);
    });
  });
}

// Example usage:
// 
// import { predictRent } from "./actions";
// 
// const predictions = await predictRent({
//   workLocation: { lat: 51.5074, lng: -0.1278 },
//   commuteTimeMinutes: 30,
//   commuteType: "drive",
//   rentOption: 2
// });
