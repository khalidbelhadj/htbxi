import pandas as pd
import requests
import logging

def is_numeric(value):
    try:
        float(value)
        return True
    except ValueError:
        return False
    
def get_district_names():
    raw_data = pd.ExcelFile('data/rent_data.xlsx')
    district_data = raw_data.parse('3', skiprows=2, names=['District', 'Category', 'Count', 'Mean', 'LowerQ', 'Median', 'UpperQ'])
    return district_data['District'].unique()

def get_rent_data(file_path = 'data/rent_data.xlsx'):
    raw_data = pd.ExcelFile(file_path)
    district_data = raw_data.parse('3', skiprows=2, names=['District', 'Category', 'Count', 'Mean', 'LowerQ', 'Median', 'UpperQ'])
    district_data['Mean'] = district_data[district_data['Mean'].apply(is_numeric)]['Mean']
    district_data['LowerQ'] = district_data[district_data['LowerQ'].apply(is_numeric)]['LowerQ']
    district_data['Median'] = district_data[district_data['Median'].apply(is_numeric)]['Median']
    district_data['UpperQ'] = district_data[district_data['UpperQ'].apply(is_numeric)]['UpperQ']
    burrough_data = raw_data.parse('2', skiprows=2, names=['Burrough', 'Category', 'Count', 'Mean', 'LowerQ', 'Median', 'UpperQ'])
    burrough_data['Mean'] = burrough_data[burrough_data['Mean'].apply(is_numeric)]['Mean']
    burrough_data['LowerQ'] = burrough_data[burrough_data['LowerQ'].apply(is_numeric)]['LowerQ']
    burrough_data['Median'] = burrough_data[burrough_data['Median'].apply(is_numeric)]['Median']
    burrough_data['UpperQ'] = burrough_data[burrough_data['UpperQ'].apply(is_numeric)]['UpperQ']
    # only take where category is 'One Bedroom' or 'Studio' and merge the categories
    district_data = district_data[district_data['Category'].isin(['One Bedroom', 'Studio'])]
    burrough_data = burrough_data[burrough_data['Category'].isin(['One Bedroom', 'Studio'])]
    district_data['Category'] = district_data['Category'].apply(lambda x: 'One Bedroom' if x == '1 Bedroom' else 'Studio')
    burrough_data['Category'] = burrough_data['Category'].apply(lambda x: 'One Bedroom' if x == '1 Bedroom' else 'Studio')
    # merge the categories
    district_data = district_data.groupby(['District', 'Category']).agg({'Mean': 'mean', 'LowerQ': 'mean', 'Median': 'mean', 'UpperQ': 'mean'}).reset_index()
    burrough_data = burrough_data.groupby(['Burrough', 'Category']).agg({'Mean': 'mean', 'LowerQ': 'mean', 'Median': 'mean', 'UpperQ': 'mean'}).reset_index()
    return district_data, burrough_data

def get_burrough_by_district(district):
    url = f"https://api.postcodes.io/outcodes/{district}"
    response = requests.get(url)
    response.raise_for_status()  # Raise exception for bad status codes
    try:
        return response.json()["result"]["admin_district"]
    except:
        return response.json()["result"][0]["admin_district"]

def get_rent_by_burrough(rent_data, burroughs):
    # try first burrough thats in our data
    for burrough in burroughs:
        if burrough in rent_data['Burrough'].values:
            return rent_data[rent_data['Burrough'] == burrough]["Mean"].values[0]
    
def get_rent_by_district(district):
    district_data, burrough_data = get_rent_data()
    # if any of the 'Mean' values in the district data are not None or NaN, return the mean value from the district data
    if any(district_data[district_data['District'] == district]["Mean"].notna()):
        return district_data[district_data['District'] == district]["Mean"].values[0]
    else:
        return get_rent_by_burrough(burrough_data, get_burrough_by_district(district))
    
def get_district_from_coords(lat, lon):
    url = f"https://api.postcodes.io/postcodes?lon={lon}&lat={lat}"
    response = requests.get(url)
    response.raise_for_status()  # Raise exception for bad status codes
    try:
        return response.json()["result"]["outcode"]
    except:
        if len(response.json()["result"]) > 0:
            return response.json()["result"][0]["outcode"]
        else:
            return None
        
def get_rent_range(rent):
    """
    :rent: int - 1 - Lower, 2 - Median, 3 - Upper
    """
    # get rent Upper, Lower and Median
    district_data, burrough_data = get_rent_data()
    min_rent = 0
    max_rent = 10000
    if rent == 1:
        max_rent = (district_data['LowerQ'].mean() + burrough_data['LowerQ'].mean()) / 2
        min_rent = 500
    elif rent == 2:
        max_rent = (district_data['Median'].mean() + burrough_data['Median'].mean()) / 2
        min_rent = 700
    elif rent == 3:
        max_rent = (district_data['UpperQ'].mean() + burrough_data['UpperQ'].mean()) / 2
        min_rent = 1000

    return min_rent, max_rent