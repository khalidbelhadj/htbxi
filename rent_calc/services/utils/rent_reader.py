import pandas as pd
import requests

def get_rent_data(file_path = 'data/rent_data.xlsx'):
    raw_data = pd.ExcelFile(file_path)
    district_data = raw_data.parse('3', skiprows=2, names=['District', 'Category', 'Count', 'Mean', 'LowerQ', 'Median', 'UpperQ'])
    burrough_data = raw_data.parse('2', skiprows=2, names=['Burrough', 'Category', 'Count', 'Mean', 'LowerQ', 'Median', 'UpperQ'])
    return district_data, burrough_data

def get_burrough_by_district(district):
    url = f"https://api.postcodes.io/outcodes/{district}"
    
    response = requests.get(url)
    response.raise_for_status()  # Raise exception for bad status codes
    try:
        return response.json()["result"][0]["admin_district"]
    except:
        return response.json()["result"]["admin_county"]

def get_rent_by_district(rent_data, district):
    return rent_data[rent_data['District'] == district]

def get_rent_by_burrough(rent_data, burroughs):
    # try first burrough thats in our data
    for burrough in burroughs:
        if burrough in rent_data['Burrough']:
            return rent_data[rent_data['Burrough'] == burrough]
    
def get_rent_by_district(district):
    district_data, burrough_data = get_rent_data()

    if input_district in district_data['District'].values:
        return get_rent_by_district(district_data, input_district)
    else:
        return get_rent_by_burrough(burrough_data, get_burrough_by_district(input_district))

if __name__ == '__main__':
    input_district = "BR1"
    get_rent_by_district(input_district)