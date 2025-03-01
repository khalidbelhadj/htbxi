"use client";

import { Search } from "lucide-react";
import { useState } from "react";
import Map from "react-map-gl/mapbox";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import WorkLocation from "@/components/work-location";
import CommutePopover from "@/components/commute-popover";

export default function Home() {
  const [commuteTime, setCommuteTime] = useState(30);
  const [transportMode, setTransportMode] = useState<
    "walk" | "drive" | "public"
  >("drive");

  const handleTransportModeChange = (mode: "walk" | "drive" | "public") => {
    setTransportMode(mode);
  };

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
          <div className="">Rent</div>
          <Separator orientation="vertical" />
          <Button variant="ghost" className="!p-0 size-10">
            <Search className="text-ring size-5" />
          </Button>
        </div>
      </div>

      <Map
        mapboxAccessToken="pk.eyJ1Ijoia2hhbGlkYmVsaGFkaiIsImEiOiJjbTdxZTJuZmowdjNsMmtyM2V4d2MzbGIwIn0.rM356YxasCs7OYPymA-ZDQ"
        initialViewState={{
          longitude: -0.14213677752282086,
          latitude: 51.50448489745423,
          zoom: 9.5,
        }}
        style={{ width: "100%", height: "100%" }}
        mapStyle="mapbox://styles/mapbox/streets-v9"
      />
    </div>
  );
}
