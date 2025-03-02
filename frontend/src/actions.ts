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
