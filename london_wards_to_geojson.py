import geopandas as gpd
import requests
import os
from pathlib import Path

def download_london_wards():
    """
    Downloads London wards data from the London Datastore.
    Returns the path to the downloaded file.
    """
    # URL for London wards (Statistical GIS Boundary Files)
    url = "https://data.london.gov.uk/download/statistical-gis-boundary-files-london/9ba8c833-6370-4b11-abdc-314aa020d5e0/statistical-gis-boundaries-london.zip"
    
    # Create a data directory if it doesn't exist
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    # Download the zip file
    print("Downloading London wards data...")
    response = requests.get(url)
    zip_path = data_dir / "london_wards.zip"
    
    with open(zip_path, 'wb') as f:
        f.write(response.content)
    
    return zip_path

def convert_to_geojson(shapefile_path, output_file):
    """
    Converts shapefile to GeoJSON format.
    """
    # Read the shapefile using geopandas
    print(f"Reading shapefile from {shapefile_path}")
    gdf = gpd.read_file(shapefile_path)
    
    # Convert to GeoJSON
    print(f"Converting to GeoJSON and saving to {output_file}")
    gdf.to_file(output_file, driver='GeoJSON')
    
    print("Conversion completed successfully!")

def main():
    try:
        # Download the data
        zip_path = download_london_wards()
        
        # Extract the zip file
        import zipfile
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall("data")
        
        # Find the ward shapefile
        shapefile_path = None
        for root, dirs, files in os.walk("data"):
            for file in files:
                if file.endswith(".shp") and "ward" in file.lower():
                    shapefile_path = os.path.join(root, file)
                    break
        
        if shapefile_path is None:
            raise Exception("Could not find ward shapefile in the downloaded data")
        
        # Convert to GeoJSON
        output_file = "london_wards.geojson"
        convert_to_geojson(shapefile_path, output_file)
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main() 