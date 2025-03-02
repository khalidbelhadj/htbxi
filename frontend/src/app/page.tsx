"use client";

import { Car, HomeIcon, Search, Shield, Train, Bike } from "lucide-react";
import { useState, useRef, useEffect } from "react";
import mapboxgl, { LngLat } from "mapbox-gl";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import WorkLocation from "@/components/work-location";
import CommutePopover from "@/components/commute-popover";
import RentPopover from "@/components/rent-popover";
import SalaryPopover from "@/components/salary-popover";
import { getPredictions, query } from "@/actions";
import { useMutation } from "@tanstack/react-query";
import { AnimatePresence, motion } from "framer-motion";
import { cn } from "@/lib/utils";
import { toast } from "sonner";
import SalaryPieChart from "@/components/salary-pie-chart";

export default function Home() {
  const [commuteTime, setCommuteTime] = useState(30);
  const [transportMode, setTransportMode] = useState<
    "bike" | "drive" | "public"
  >("drive");
  const [rent, setRent] = useState<1 | 2 | 3>(1);
  const [salary, setSalary] = useState(50000);

  const mapContainerRef = useRef<HTMLDivElement>(null);
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const markerRef = useRef<mapboxgl.Marker | null>(null);
  const selectedFeatureRef = useRef(false);
  const [hoveredFeature, setHoveredFeature] = useState<GeoJSON.Feature | null>(
    null
  );

  const [selectedFeature, setSelectedFeature] = useState(false);

  // Update the ref whenever the state changes
  useEffect(() => {
    selectedFeatureRef.current = selectedFeature;
  }, [selectedFeature]);

  const handleTransportModeChange = (mode: "bike" | "drive" | "public") => {
    setTransportMode(mode);
  };

  const handleRentChange = (value: number) => {
    setRent(value as 1 | 2 | 3);
  };

  const handleSalaryChange = (value: number) => {
    setSalary(value);
  };

  const { mutate: search, data: searchResults } = useMutation({
    mutationFn: async () => {
      if (!workLocation) {
        toast.error("Please select a work location");
        return;
      }
      // const results = await query(workLocation, transportMode, rent);
      const results = await getPredictions(
        workLocation.lng,
        workLocation.lat,
        transportMode,
        rent,
        commuteTime
      );

      console.log(results);
      alert("results");
      const map = new Map();

      for (const result of results) {
        map.set(result.code, result);
      }

      return map;
    },
    onSuccess: async (data) => {
      if (!data || !mapRef.current) return;

      // Extract the area codes from the results
      const areaCodes = Array.from(data.keys());

      // If we haven't loaded the GeoJSON data yet, load it now
      if (!mapRef.current.getSource("areas-source")) {
        // Fetch the GeoJSON data
        const geoJsonData = await fetch("/result.geojson").then((r) =>
          r.json()
        );

        // Add source for the entire feature collection
        mapRef.current.addSource("areas-source", {
          type: "geojson",
          data: geoJsonData,
        });

        // Add the default layer for features
        mapRef.current.addLayer({
          id: "areas-layer",
          type: "fill",
          source: "areas-source",
          paint: {
            "fill-color": "#0091cd",
            "fill-opacity": 0.2,
          },
          filter: ["in", ["get", "name"], ["literal", areaCodes]],
        });

        // Add outline layer
        mapRef.current.addLayer({
          id: "areas-outline",
          type: "line",
          source: "areas-source",
          paint: {
            "line-color": "#0091cd",
            "line-width": 1,
          },
          filter: ["in", ["get", "name"], ["literal", areaCodes]],
        });

        // Add hover layer
        mapRef.current.addLayer({
          id: "areas-hover",
          type: "fill",
          source: "areas-source",
          paint: {
            "fill-color": "#0091cd",
            "fill-opacity": 0.5, // Higher opacity for hover state
          },
          filter: ["==", "name", ""], // Initially no features are shown in hover state
        });

        // Set up event handlers for hover effects
        setupHoverEffects();
      } else {
        // If we already have the source, just update the filters
        mapRef.current.setFilter("areas-layer", [
          "in",
          ["get", "name"],
          ["literal", areaCodes],
        ]);
        mapRef.current.setFilter("areas-outline", [
          "in",
          ["get", "name"],
          ["literal", areaCodes],
        ]);
      }
    },
  });

  const handleSearch = async () => {
    search();
  };

  const [workLocation, setWorkLocation] = useState<LngLat | null>(null);

  useEffect(() => {
    if (mapRef.current) return; // Initialize map only once

    if (!mapContainerRef.current) return; // Safety check

    // Initialize map
    mapRef.current = new mapboxgl.Map({
      accessToken: process.env.NEXT_PUBLIC_MAPBOX_TOKEN,
      container: mapContainerRef.current,
      style: "mapbox://styles/mapbox/streets-v12/",
      // center: [-0.14213677752282086, 51.50448489745423],
      center: [-0.071798195434898, 51.426286250396288],
      zoom: 9.5,
    });

    // Add navigation controls
    mapRef.current.addControl(new mapboxgl.NavigationControl(), "top-right");

    // No longer loading GeoJSON data or adding layers here
    // We'll do that when we get search results
  }, []); // Empty dependency array ensures this runs once on mount

  // Function to set up hover effects
  const setupHoverEffects = () => {
    if (!mapRef.current) return;

    // Track the currently hovered feature ID
    let hoveredFeatureId: string | null = null;

    // When mouse moves, update the hover layer
    mapRef.current.on("mousemove", (e) => {
      if (!mapRef.current) return;

      // Don't allow hovering on other features when something is selected
      if (selectedFeatureRef.current) return;

      // Query features under the mouse
      const features = mapRef.current.queryRenderedFeatures(e.point, {
        layers: ["areas-layer"],
      });

      // Change the cursor style to pointer if hovering over a feature
      mapRef.current.getCanvas().style.cursor = features.length
        ? "pointer"
        : "";

      // If there's a feature under the mouse
      if (features.length > 0) {
        const feature = features[0];

        const featureId = feature.properties?.name as string;
        if (!selectedFeatureRef.current) {
          setHoveredFeature(feature);
        }

        // If we're hovering over a new feature
        if (hoveredFeatureId !== featureId) {
          // If we were previously hovering over a feature, reset it
          if (hoveredFeatureId) {
            mapRef.current.setFilter("areas-hover", ["==", "name", ""]);
          }

          // Set the new hovered feature
          hoveredFeatureId = featureId;

          // Update the hover layer to show only this feature
          mapRef.current.setFilter("areas-hover", ["==", "name", featureId]);
        }
      } else {
        // If we're not hovering over any feature, reset the hover layer
        if (hoveredFeatureId) {
          mapRef.current.setFilter("areas-hover", ["==", "name", ""]);
          hoveredFeatureId = null;
        }

        if (!selectedFeatureRef.current) {
          setHoveredFeature(null);
        }
      }
    });

    // Reset hover state when mouse leaves the map
    mapRef.current.on("mouseleave", "areas-layer", () => {
      if (!mapRef.current || selectedFeatureRef.current) return;

      mapRef.current.getCanvas().style.cursor = "";

      if (hoveredFeatureId) {
        mapRef.current.setFilter("areas-hover", ["==", "name", ""]);
        hoveredFeatureId = null;
      }

      if (!selectedFeatureRef.current) {
        setHoveredFeature(null);
      }
    });

    mapRef.current.on("click", "areas-layer", (e) => {
      const features = mapRef.current?.queryRenderedFeatures(e.point, {
        layers: ["areas-layer"],
      });

      if (!features) return;
      if (features.length > 0) {
        // Toggle selection state
        setSelectedFeature(!selectedFeatureRef.current);
      }
    });

    // Add a click handler for the map background to deselect
    mapRef.current.on("click", (e) => {
      const features = mapRef.current?.queryRenderedFeatures(e.point, {
        layers: ["areas-layer"],
      });

      // If we clicked outside any feature, deselect
      if (!features || features.length === 0) {
        setSelectedFeature(false);
      }
    });
  };

  useEffect(() => {
    if (mapRef.current && workLocation) {
      mapRef.current.flyTo({
        center: [workLocation.lng, workLocation.lat],
      });

      // Remove existing marker if it exists
      if (markerRef.current) {
        markerRef.current.remove();
      }

      // Create a new marker
      markerRef.current = new mapboxgl.Marker({
        color: "#FF0000", // Red color
      })
        .setLngLat([workLocation.lng, workLocation.lat])
        .addTo(mapRef.current);
    }
  }, [workLocation]);

  const hoverFeatureInfo = searchResults?.get(hoveredFeature?.properties?.name);

  // const hoverFeatureInfo = {
  //   code: "SE7",
  //   commute: 20,
  //   commuteMode: "walk",
  //   commuteRating: 2,
  //   rent: 2000,
  //   rentRating: 1,
  //   crime: 5,
  // };

  return (
    <div className="w-screen h-screen relative">
      {/* Feature on top left corner */}
      <AnimatePresence>
        {hoverFeatureInfo && (
          <motion.div
            variants={{
              hidden: {
                opacity: 0,
                left: "50%",
                transform: "translateX(-50%)",
                top: "auto",
                bottom: "1rem",
                width: "15rem",
              },
              visible: {
                opacity: 1,
                left: "50%",
                transform: "translateX(-50%)",
                top: "auto",
                bottom: "1rem",
                width: "15rem",
              },
              expanded: {
                opacity: 1,
                left: "2rem",
                transform: "translateX(0)",
                top: "5rem",
                width: "30rem",
              },
            }}
            initial="hidden"
            animate={selectedFeature ? "expanded" : "visible"}
            exit="hidden"
            className="absolute bottom-2 bg-background rounded-md p-0 z-20 ring-1 ring-ring flex flex-col gap-2"
          >
            <div className="flex flex-col gap-2 p-2">
              <div className="text-lg font-medium">{hoverFeatureInfo.code}</div>
              {hoverFeatureInfo && (
                <div className="text-sm text-muted-foreground flex gap-2">
                  <div
                    className={cn(
                      "w-fit ring-1 rounded-full px-1 ring-ring/50 flex items-center gap-1 justify-center",
                      hoverFeatureInfo.commuteRating == 4 &&
                        "bg-green-100 ring-green-400",
                      hoverFeatureInfo.commuteRating == 3 && "bg-background",
                      hoverFeatureInfo.commuteRating == 2 &&
                        "bg-yellow-100 ring-yellow-400",
                      hoverFeatureInfo.commuteRating == 1 &&
                        "bg-red-100 ring-red-400"
                    )}
                  >
                    {hoverFeatureInfo.commuteMode === "drive" && (
                      <Car className="size-3" />
                    )}
                    {hoverFeatureInfo.commuteMode === "public" && (
                      <Train className="size-3" />
                    )}
                    {hoverFeatureInfo.commuteMode === "walk" && (
                      <Bike className="size-3" />
                    )}

                    {hoverFeatureInfo?.commute}
                  </div>
                  <div
                    className={cn(
                      "w-fit ring-1 rounded-full px-1 ring-ring/50 flex items-center gap-1 justify-center",
                      hoverFeatureInfo.rentRating == 4 &&
                        "bg-green-100 ring-green-400",
                      hoverFeatureInfo.rentRating == 3 && "bg-background",
                      hoverFeatureInfo.rentRating == 2 &&
                        "bg-yellow-100 ring-yellow-400",
                      hoverFeatureInfo.rentRating == 1 &&
                        "bg-red-100 ring-red-400"
                    )}
                  >
                    <HomeIcon className="size-3" />£{hoverFeatureInfo?.rent}
                    /month
                  </div>
                  <div
                    className={cn(
                      "w-fit ring-1 rounded-full px-1 ring-ring/50 flex items-center gap-1 justify-center",
                      hoverFeatureInfo.crime == 4 &&
                        "bg-green-100 ring-green-400",
                      hoverFeatureInfo.crime == 3 && "bg-background",
                      hoverFeatureInfo.crime == 2 &&
                        "bg-yellow-100 ring-yellow-400",
                      hoverFeatureInfo.crime == 1 && "bg-red-100 ring-red-400"
                    )}
                  >
                    <Shield className="size-3" />

                    {hoverFeatureInfo?.crime}
                  </div>
                </div>
              )}
            </div>
            {selectedFeature && <SalaryPieChart salary={salary} />}
          </motion.div>
        )}
      </AnimatePresence>
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
          <SalaryPopover salary={salary} onSalaryChange={handleSalaryChange} />
          <Separator orientation="vertical" />
          <Button variant="ghost" className="py-0 !px-4" onClick={handleSearch}>
            <Search className="text-ring size-5" />
          </Button>
        </div>
      </div>
      <div ref={mapContainerRef} className="w-full h-full" />
    </div>
  );
}
