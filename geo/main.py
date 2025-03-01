# 51.49541° N, 0.13154° W

# GEThttps://api.postcodes.io/outcodes?lon=:longitude&lat=:latitude

import requests

# Coordinates for London (Westminster)
LATITUDE = 51.49541
LONGITUDE = -0.13154  # Note: W is negative longitude

def get_postcodes_by_coordinates(latitude: float, longitude: float) -> dict:
    """
    Fetch postcode data for given coordinates using postcodes.io API
    
    Args:
        latitude (float): Latitude coordinate
        longitude (float): Longitude coordinate
        
    Returns:
        dict: API response containing postcode data
    """
    url = f"https://api.postcodes.io/outcodes"
    params = {
        "lon": longitude,
        "lat": latitude,
        "radius": "400"
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise exception for bad status codes
    return response.json()

def format_list_field(field: list) -> str:
    """Format a list field for display, handling empty lists."""
    if not field:
        return "None"
    return ", ".join(field)

def main():
    try:
        result = get_postcodes_by_coordinates(LATITUDE, LONGITUDE)
        print("\nNearby postcodes data:")
        
        if result["result"]:
            for outcode in result["result"]:
                print("\n" + "=" * 50)
                print(f"Outcode: {outcode['outcode']}")
                # print("-" * 50)
                # print(f"Location:")
                # print(f"  Latitude: {outcode.get('latitude', 'N/A')}")
                # print(f"  Longitude: {outcode.get('longitude', 'N/A')}")
                # print(f"  Eastings: {outcode.get('eastings', 'N/A')}")
                # print(f"  Northings: {outcode.get('northings', 'N/A')}")
                # print("\nAdministrative Areas:")
                # print(f"  Counties: {format_list_field(outcode.get('admin_county', []))}")
                print(f"  Districts: {format_list_field(outcode.get('admin_district', []))}")
                # print(f"  Wards: {format_list_field(outcode.get('admin_ward', []))}")
                # print(f"  Parishes: {format_list_field(outcode.get('parish', []))}")
                # print(f"  Countries: {format_list_field(outcode.get('country', []))}")
        else:
            print("No postcodes found for these coordinates.")
        
        print(f"Total of {len(result['result'])} postcodes found")
            
    except requests.RequestException as e:
        print(f"Error fetching postcode data: {e}")
    except KeyError as e:
        print(f"Unexpected response format: {e}")

if __name__ == "__main__":
    main()

