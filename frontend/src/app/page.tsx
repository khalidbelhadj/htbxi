"use client";

import { Search } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import mapboxgl from "mapbox-gl";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import WorkLocation from "@/components/work-location";
import { LngLat } from "@/types";
import CommutePopover from "@/components/commute-popover";

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

  const [workLocation, setWorkLocation] = useState<LngLat | null>(null);

  useEffect(() => {
    if (workLocation) {
      console.log(workLocation);
    }
  }, [workLocation]);

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

  useEffect(() => {
    if (mapRef.current && workLocation) {
      console.log(workLocation);
      mapRef.current.flyTo({
        center: [workLocation[0], workLocation[1]],
      });
    }
  }, [workLocation]);

  return (
    <div className="w-screen h-screen relative">
      <div className="w-full flex items-center justify-center absolute p-5 z-10">
        <div className="bg-background rounded-full flex h-12 items-center ring-ring ring-1 px-5 py-3 gap-5">
          <WorkLocation setWorkLocation={setWorkLocation} />
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
