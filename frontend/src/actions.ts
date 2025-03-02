"use server";

import { LngLat } from "mapbox-gl";

type QueryResult = {
  code: string;
  commute: number;
  rent: number;
  crime: number;
  commuteMode: "drive" | "bike" | "public";
  commuteRating: number;
  rentRating: number;
};

export async function query(
  workingLocation: LngLat,
  transport_mode: "bike" | "drive" | "public",
  rent: 1 | 2 | 3
) {
  return [
    {
      code: "SE6",
      commute: 10,
      commuteMode: "drive",
      commuteRating: 4,
      rent: 1500,
      rentRating: 1,
      crime: 1,
    },
    {
      code: "SE7",
      commute: 20,
      commuteMode: "drive",
      commuteRating: 2,
      rent: 2000,
      rentRating: 1,
      crime: 5,
    },
    {
      code: "SE8",
      commute: 30,
      commuteMode: "drive",
      commuteRating: 1,
      rent: 2500,
      rentRating: 1,
      crime: 3,
    },
  ] as QueryResult[];
}

export async function getPredictions(
  lng: number,
  lat: number,
  transport_mode: "bike" | "drive" | "public",
  rent: 1 | 2 | 3,
  max_travel_time: number
) {
  // console.log(lng, lat, transportMode, rent, max_travel_time);

  const response = await fetch(`http://127.0.0.1:5000/predict`, {
    method: "POST",
    body: JSON.stringify({
      longitude: lng,
      latitude: lat,
      transport_mode,
      min_rent: rent === 1 ? 1000 : rent === 2 ? 2000 : 3000,
      max_rent: rent === 1 ? 2000 : rent === 2 ? 3000 : 4000,
      max_travel_time,
    }),
    headers: {
      "Content-Type": "application/json",
      Accept: "application/json",
    },
  });

  const data = await response.json();
  console.log(data);

  // extend this data to have random crime, commute, and rent ratings
  const extendedData = data.map((item: QueryResult) => ({
    ...item,
    crimeRating: Math.floor(Math.random() * 5) + 1,
    commuteRating: Math.floor(Math.random() * 5) + 1,
    rentRating: Math.floor(Math.random() * 5) + 1,
  }));
  return extendedData;
}
