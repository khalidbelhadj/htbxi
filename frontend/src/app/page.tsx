"use client";

import { Input } from "@/components/ui/input";
import { Search } from "lucide-react";
import { useState } from "react";
import Map from "react-map-gl/mapbox";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";

import { Label } from "@/components/ui/label";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Slider } from "@/components/ui/slider";
import { Car, Train, FootprintsIcon as Walk } from "lucide-react";

export default function Home() {
  const [commuteTime, setCommuteTime] = useState(30);
  const [transportMode, setTransportMode] = useState<
    "walk" | "drive" | "public"
  >("drive");

  const formatTime = (minutes: number) => {
    if (minutes < 60) {
      return `${minutes} minutes`;
    } else {
      return "1 hour";
    }
  };

  const handleTransportModeChange = (mode: "walk" | "drive" | "public") => {
    setTransportMode(mode);
  };

  return (
    <div className="w-screen h-screen relative">
      <div className="w-full flex items-center justify-center absolute p-5 z-10">
        <div className="bg-background rounded-full flex h-12 items-center ring-ring ring-1 px-5 py-3 gap-5 text-lg">
          <Input
            placeholder="Work location..."
            className="focus-visible:ring-0 focus-within:border-none shadow-none border-none h-full w-[15rem] p-1 !text-lg"
          />
          <Separator orientation="vertical" />
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className="w-64 justify-start">
                {transportMode === "walk" && <Walk className="mr-2 h-4 w-4" />}
                {transportMode === "drive" && <Car className="mr-2 h-4 w-4" />}
                {transportMode === "public" && (
                  <Train className="mr-2 h-4 w-4" />
                )}
                <span>Commute: {formatTime(commuteTime)}</span>
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-80">
              <div className="grid gap-4">
                <div className="space-y-2">
                  <h4 className="font-medium leading-none">Commute Time</h4>
                  <p className="text-sm text-muted-foreground">
                    Set your maximum acceptable commute time.
                  </p>
                </div>
                <div className="flex justify-center space-x-2">
                  <Button
                    variant={transportMode === "walk" ? "default" : "outline"}
                    size="icon"
                    onClick={() => handleTransportModeChange("walk")}
                  >
                    <Walk className="h-4 w-4" />
                    <span className="sr-only">Walking</span>
                  </Button>
                  <Button
                    variant={transportMode === "drive" ? "default" : "outline"}
                    size="icon"
                    onClick={() => handleTransportModeChange("drive")}
                  >
                    <Car className="h-4 w-4" />
                    <span className="sr-only">Driving</span>
                  </Button>
                  <Button
                    variant={transportMode === "public" ? "default" : "outline"}
                    size="icon"
                    onClick={() => handleTransportModeChange("public")}
                  >
                    <Train className="h-4 w-4" />
                    <span className="sr-only">Public Transport</span>
                  </Button>
                </div>
                <div className="grid gap-4">
                  <div className="grid gap-2">
                    <div className="flex justify-between">
                      <Label htmlFor="commute-time">
                        Time: {formatTime(commuteTime)}
                      </Label>
                    </div>
                    <Slider
                      id="commute-time"
                      min={5}
                      max={60}
                      step={5}
                      value={[commuteTime]}
                      onValueChange={(value) => setCommuteTime(value[0])}
                      className="py-4"
                    />
                    <div className="flex justify-between text-xs text-muted-foreground">
                      <span>5 min</span>
                      <span>30 min</span>
                      <span>1 hour</span>
                    </div>
                  </div>
                </div>
              </div>
            </PopoverContent>
          </Popover>
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
