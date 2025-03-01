"use client";

import { Search } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import mapboxgl from "mapbox-gl";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import WorkLocation from "@/components/work-location";
import CommutePopover from "@/components/commute-popover";
import RentPopover from "@/components/rent-popover";

import "mapbox-gl/dist/mapbox-gl.css";

// Set mapbox access token
mapboxgl.accessToken =
  "pk.eyJ1Ijoia2hhbGlkYmVsaGFkaiIsImEiOiJjbTdxZTJuZmowdjNsMmtyM2V4d2MzbGIwIn0.rM356YxasCs7OYPymA-ZDQ";

// Define the GeoJSON data
const mainePolygon = {
  type: "Feature" as const,
  geometry: {
    type: "Polygon" as const,
    // These coordinates outline Maine.
    coordinates: [
      [
        [-67.13734, 45.13745],
        [-66.96466, 44.8097],
        [-68.03252, 44.3252],
        [-69.06, 43.98],
        [-70.11617, 43.68405],
        [-70.64573, 43.09008],
        [-70.75102, 43.08003],
        [-70.79761, 43.21973],
        [-70.98176, 43.36789],
        [-70.94416, 43.46633],
        [-71.08482, 45.30524],
        [-70.66002, 45.46022],
        [-70.30495, 45.91479],
        [-70.00014, 46.69317],
        [-69.23708, 47.44777],
        [-68.90478, 47.18479],
        [-68.2343, 47.35462],
        [-67.79035, 47.06624],
        [-67.79141, 45.70258],
        [-67.13734, 45.13745],
      ],
    ],
  },
  properties: {},
};

export default function Home() {
  const [commuteTime, setCommuteTime] = useState(30);
  const [transportMode, setTransportMode] = useState<
    "walk" | "drive" | "public"
  >("drive");
  const [rent, setRent] = useState<1 | 2 | 3>(1);

  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);

  const handleTransportModeChange = (mode: "walk" | "drive" | "public") => {
    setTransportMode(mode);
  };

  const handleRentChange = (value: number) => {
    setRent(value as 1 | 2 | 3);
  };

  useEffect(() => {
    if (mapRef.current) return; // Initialize map only once

    if (!mapContainerRef.current) return; // Safety check

    // Initialize map
    mapRef.current = new mapboxgl.Map({
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/streets-v9",
      center: [-0.14213677752282086, 51.50448489745423],
      zoom: 9.5,
    });

    // Add navigation controls
    mapRef.current.addControl(new mapboxgl.NavigationControl(), "top-right");

    // When map loads, add the polygon source and layer
    mapRef.current.on("load", () => {
      if (!mapRef.current) return;

      // Add source for the polygon
      mapRef.current.addSource("maine", {
        type: "geojson",
        data: mainePolygon,
      });

      // Add a layer showing the polygon
      mapRef.current.addLayer({
        id: "maine",
        type: "fill",
        source: "maine",
        paint: {
          "fill-color": "#0091cd",
          "fill-opacity": 0.2,
        },
      });
    });

    // Clean up on unmount
    return () => {
      if (mapRef.current) {
        mapRef.current.remove();
        mapRef.current = null;
      }
    };
  }, []); // Empty dependency array ensures this runs once on mount

  return (
    <div className="w-screen h-screen relative">
      <div className="w-full flex items-center justify-center absolute p-5 z-10">
        <div className="bg-background rounded-full flex h-12 items-center ring-ring ring-1 px-5 py-3 gap-5">
          <WorkLocation />
          <Separator orientation="vertical" />
          <CommutePopover
            commuteTime={commuteTime}
            transportMode={transportMode}
            onCommuteTimeChange={setCommuteTime}
            onTransportModeChange={handleTransportModeChange}
          />
          <Separator orientation="vertical" />
          <RentPopover rent={rent} onRentChnge={handleRentChange} />
          <Separator orientation="vertical" />
          <Button variant="ghost" className="py-0 !px-4">
            <Search className="text-ring size-5" />
          </Button>
        </div>
      </div>

      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
}
