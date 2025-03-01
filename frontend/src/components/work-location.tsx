"use client";

import { useEffect, useState } from "react";
import { Input } from "./ui/input";
import { LngLat } from "@/types";
import { Popover, PopoverContent, PopoverTrigger } from "./ui/popover";
import { ChevronsUpDown } from "lucide-react";

type Props = {
  setWorkLocation?: (workLocation: LngLat) => void;
};

type SearchResult = {
  name: string;
  place_formatted: string;
  coordinates: LngLat;
};

type MapboxSuggestion = {
  name: string;
  place_formatted: string;
  mapbox_id: string;
};

type MapboxResponse = {
  suggestions: MapboxSuggestion[];
};

export default function WorkLocation({ setWorkLocation }: Props) {
  const [open, setOpen] = useState(false);
  const [selectedValue, setSelectedValue] = useState("");
  const [sessionToken, setSessionToken] = useState("");
  const [searchResults, setSearchResults] = useState<MapboxSuggestion[]>([]); 
  const [searchValue, setSearchValue] = useState("");

  useEffect(() => {
    const token = crypto.randomUUID();
    setSessionToken(token);
  }, []);

  useEffect(() => {
    const searchPlaces = async () => {
      if (!searchValue) {
        setSearchResults([]);
        return;
      }

      try {
        // 51.5072° N, 0.1276° W
        const londonCoords = "0.1276, 51.5072";
        const response = await fetch(
          `https://api.mapbox.com/search/searchbox/v1/suggest?q=${encodeURIComponent(
            searchValue
          )}
          &session_token=${sessionToken}&access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}&proximity=${londonCoords}
          `

        );

        const data = await response.json() as MapboxResponse;
        const suggestions = data.suggestions.map((suggestion: MapboxSuggestion) => ({
          name: suggestion.name,
          place_formatted: suggestion.place_formatted,
          mapbox_id: suggestion.mapbox_id,
        }));

        setSearchResults(suggestions);
      } catch (error) {
        console.error("Error fetching search results:", error);
      }
    };

    const debounceTimeout = setTimeout(searchPlaces, 300);
    return () => clearTimeout(debounceTimeout);
  }, [searchValue, sessionToken]);

  const handleSelect = (placeFormatted: string, coordinates: LngLat) => {
    setSelectedValue(placeFormatted);
    setSearchValue("");
    setOpen(false);
    if (setWorkLocation) {
      console.log('setting work location', coordinates);
      setWorkLocation(coordinates);
    }
  };

  return (
    <Popover open={open} onOpenChange={setOpen}>
      <PopoverTrigger asChild>
        <div className="flex items-center">
          <Input
            value={selectedValue}
            placeholder="Work location..."
            className="focus-visible:ring-0 focus-within:border-none shadow-none border-none h-full w-[15rem] p-1"
            readOnly
          />
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </div>
      </PopoverTrigger>
      <PopoverContent className="w-[400px] p-0" align="start">
        <Input
          placeholder="Search for a location..."
          className="focus-visible:ring-0 focus-within:border-none shadow-none border-none h-full w-full p-1"
          value={searchValue}
          onChange={(e) => setSearchValue(e.target.value)}
        />
        <ul className="max-h-[300px] overflow-y-auto">
          {searchResults.map((result) => (
            <li key={result.mapbox_id}>
              <button
                className="w-full text-left px-2 py-3 hover:bg-accent cursor-pointer"
                onClick={async () => {
                  // TODO: Retrieve coordinates for the selected location
                  // https://api.mapbox.com/search/searchbox/v1/retrieve/{id}
                  const response = await fetch(
                    `https://api.mapbox.com/search/searchbox/v1/retrieve/${result.mapbox_id}?session_token=${sessionToken}&access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}`
                  );
                  const data = await response.json();
                  const coordinates = data.features[0].geometry.coordinates;
                  handleSelect(result.place_formatted, coordinates);
                }}
              >
                <div className="flex items-center gap-2">
                  <div className="text-sm text-muted-foreground">
                    {result.name}
                  </div>
                  <div className="text-sm text-muted-foreground">
                    {result.place_formatted}
                  </div>
                </div>
              </button>
            </li>
          ))}
        </ul>
      </PopoverContent>
    </Popover>
  );
}
