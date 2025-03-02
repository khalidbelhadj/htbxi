import requests
import logging



def get_postcodes_by_coordinates(latitude: float, longitude: float, radius: int = 400) -> dict:
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
        "radius": radius
    }
    
    response = requests.get(url, params=params)
    response.raise_for_status()  # Raise exception for bad status codes
    return response.json()

def format_list_field(field: list) -> str:
    """Format a list field for display, handling empty lists."""
    if not field:
        return "None"
    return ", ".join(field)

def get_district_coords(district: str) -> dict:
    url = f"https://api.postcodes.io/outcodes/{district}"
    response = requests.get(url)
    response.raise_for_status()  # Raise exception for bad status codes
    try:
        return response.json()["result"]
    except:
        return response.json()["result"][0]

def get_all_districts(_districts: list) -> dict:
    """
    Get coordinates for all districts in the list
    """
    districts = {}
    for district in _districts:
        try:
            districts[district] = get_district_coords(district)
        except Exception as e:
            logging.error(f"Failed to get coordinates for district: {district}")
            logging.error(e)
    return districts
        