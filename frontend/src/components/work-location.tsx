"use client";

import { useEffect, useState, useRef } from "react";
import { Input } from "./ui/input";
import { LngLat } from "mapbox-gl";

type Props = {
  setWorkLocation: (workLocation: LngLat) => void;
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
  const [sessionToken, setSessionToken] = useState("");
  const [searchResults, setSearchResults] = useState<MapboxSuggestion[]>([]);
  const [searchValue, setSearchValue] = useState("");
  const [isOpen, setIsOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    const token = crypto.randomUUID();
    setSessionToken(token);
  }, []);

  // Open when input is focused
  useEffect(() => {
    const handleFocus = () => {
      setIsOpen(true);
    };

    const handleBlur = () => {
      // Small delay to allow for click events on dropdown items to complete
      setTimeout(() => {
        setIsOpen(false);
      }, 200);
    };

    const inputElement = inputRef.current;
    if (inputElement) {
      inputElement.addEventListener("focus", handleFocus);
      inputElement.addEventListener("blur", handleBlur);
    }
    return () => {
      if (inputElement) {
        inputElement.removeEventListener("focus", handleFocus);
        inputElement.removeEventListener("blur", handleBlur);
      }
    };
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
        const londonBbox = "-0.646384,51.220647,0.494032,51.744038";
        const response = await fetch(
          `https://api.mapbox.com/search/searchbox/v1/suggest?q=${encodeURIComponent(
            searchValue
          )}
          &session_token=${sessionToken}&access_token=${
            process.env.NEXT_PUBLIC_MAPBOX_TOKEN
          }&proximity=${londonCoords}&bbox=${londonBbox}
          `
        );

        const data = (await response.json()) as MapboxResponse;
        const suggestions = data.suggestions.map(
          (suggestion: MapboxSuggestion) => ({
            name: suggestion.name,
            place_formatted: suggestion.place_formatted,
            mapbox_id: suggestion.mapbox_id,
          })
        );
        setSearchResults(suggestions);
      } catch (error) {
        console.error("Error fetching search results:", error);
      }
    };

    if (isOpen) {
      const debounceTimeout = setTimeout(searchPlaces, 500);
      return () => clearTimeout(debounceTimeout);
    }
  }, [searchValue, sessionToken, isOpen]);

  const handleSelect = (placeFormatted: string, coordinates: LngLat) => {
    setSearchValue(placeFormatted);
    setSearchResults([]);
    setIsOpen(false);
    setWorkLocation(coordinates);
  };

  return (
    <div className="relative">
      <Input
        ref={inputRef}
        value={searchValue}
        onChange={(e) => setSearchValue(e.target.value)}
        placeholder="Work location..."
        className="focus-visible:ring-0 focus-within:border-none shadow-none border-none h-full w-[15rem] p-1"
      />
      {isOpen && searchResults.length > 0 && (
        <ul className="overflow-y-auto absolute top-full left-0 w-80 bg-background shadow-md rounded-md border-ring border">
          {searchResults.slice(0, 5).map((result) => (
            <li key={result.mapbox_id}>
              <button
                className="w-full text-left px-2 py-3 hover:bg-accent cursor-pointer"
                onClick={async () => {
                  // TODO: Retrieve coordinates kor the selected location
                  // https://api.mapbox.com/search/searchbox/v1/retrieve/{id}
                  const response = await fetch(
                    `https://api.mapbox.com/search/searchbox/v1/retrieve/${result.mapbox_id}?session_token=${sessionToken}&access_token=${process.env.NEXT_PUBLIC_MAPBOX_TOKEN}`
                  );
                  const data = await response.json();
                  const coordinates = data.features[0].geometry.coordinates;
                  const lngLat = new LngLat(coordinates[0], coordinates[1]);

                  handleSelect(result.place_formatted, lngLat);
                }}
              >
                <div className="flex flex-col">
                  <div className="max-w-full truncate">{result.name}</div>
                  <div className="text-sm text-muted-foreground max-w-full truncate">
                    {result.place_formatted}
                  </div>
                </div>
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
