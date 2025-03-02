"use server";

import { LngLat } from "mapbox-gl";

export async function query(
  workingLocation: LngLat,
  transportMode: "walk" | "drive" | "public",
  rent: 1 | 2 | 3
) {
  return [
    {
      code: "SE6",
      commute: 10,
      rent: 1500,
      crime: 2,
    },
    {
      code: "SE7",
      commute: 20,
      rent: 2000,
      crime: 5,
    },
    {
      code: "SE8",
      commute: 30,
      rent: 2500,
      crime: 1,
    },
  ];
}


export async function getPredictions(lng: number, lat: number, transportMode: "walk" | "drive" | "public", rent: 1 | 2 | 3) {
  console.log(lng, lat, transportMode, rent)
  
  const response = await fetch(`http://127.0.0.1:5000/predict`, {
    method: 'POST',
    body: JSON.stringify({
      longitude: lng,
      latitude: lat,
      transportMode,
      rent
    }),
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  })

  const data = await response.json()
  console.log(data)
}