# santos will put code here
import pickle
import numpy as np
import requests
import logging
import time
import os
import pathlib
from concurrent.futures import ThreadPoolExecutor, as_completed

from sklearn.neighbors import KDTree

def filter_districts_by_distance(workplace_district, workplace_latitude, workplace_longitude, districts, max_travel_time, travel_cache=None):
    """
    Filter districts by travel time from the workplace district.
    If travel_cache is None, calculate distances on-the-fly using multithreading.
    """

    # Create cache directory if it doesn't exist
    cache_path = pathlib.Path(__file__).parent.resolve() / 'map_cache'
    os.makedirs(cache_path, exist_ok=True)
    
    # Build path for KD tree cache file
    kd_tree_cache_file = f"{cache_path}/districts_kd_tree.pkl"
    
    # Create nodes array for KD tree
    nodes = np.array([[float(data['latitude']), float(data['longitude'])] for _, data in districts.items()])
    district_keys = list(districts.keys())
    
    # Load or create KD tree
    kd_tree = None
    if os.path.exists(kd_tree_cache_file):
        print("Loading KD tree from cache...")
        with open(kd_tree_cache_file, 'rb') as f:
            kd_tree = pickle.load(f)
        print("Loaded KD tree from cache")
    else:
        print("Creating new KD tree...")
        kd_tree = KDTree(nodes)
        # Save to cache
        with open(kd_tree_cache_file, 'wb') as f:
            pickle.dump(kd_tree, f)
        print("Saved KD tree to cache")

    # Query the KD tree - ensure we're passing a 2D array
    query_point = np.array([[workplace_latitude, workplace_longitude]])
    _, indices = kd_tree.query(query_point, k=150)
    
    # Get the nearest districts
    nearest_district_indices = indices[0]  # Get the first row of indices
    nearest_districts = [district_keys[i] for i in nearest_district_indices]
    
    # Filter the districts dictionary to only include the nearest districts
    filtered_districts_dict = {k: v for k, v in districts.items() if k in nearest_districts}

    result_districts = {}
    
    # If no cache is provided, use on-the-fly calculation with multithreading
    if travel_cache is None:
        logging.info(f"No travel cache provided, calculating distances on-the-fly for workplace district: {workplace_district}")
        
        # Rate limiting variables
        request_timestamps = []
        requests_per_minute_limit = 499  # To be safe, staying below 500
        
        # Create a list of districts to calculate (excluding workplace district)
        district_calculations = []
        for district, data in filtered_districts_dict.items():
            if district == workplace_district:
                # For workplace district, calculate from specified workplace coordinates to district center
                district_calculations.append((workplace_latitude, workplace_longitude, 
                                            data['latitude'], data['longitude'], district))
            else:
                # For other districts, calculate from workplace district center to this district center
                district_calculations.append((districts[workplace_district]['latitude'], 
                                            districts[workplace_district]['longitude'],
                                            data['latitude'], data['longitude'], district))
        logging.info(f"Will calculate journeys to {len(district_calculations)} districts")
        print(f"    Will calculate journeys to {len(district_calculations)} districts")
        with ThreadPoolExecutor(max_workers=10) as executor:
            # Map of futures to districts
            future_to_district = {}
            start_time = time.time()
            
            for from_lat, from_lon, to_lat, to_lon, district in district_calculations:
                # Check rate limiting
                current_time = time.time()
                request_timestamps = [t for t in request_timestamps if current_time - t < 60]
                
                if len(request_timestamps) >= requests_per_minute_limit:
                    oldest_timestamp = min(request_timestamps)
                    sleep_time = 60 - (current_time - oldest_timestamp)
                    if sleep_time > 0:
                        logging.info(f"Rate limit approaching, sleeping for {sleep_time:.2f} seconds")
                        time.sleep(sleep_time)
                        current_time = time.time()
                        request_timestamps = []
                
                # Add current request timestamp
                request_timestamps.append(current_time)
                
                # Submit job to executor
                future = executor.submit(get_journey, from_lat, from_lon, to_lat, to_lon)
                future_to_district[future] = district
                break
            
            # Process completed futures
            for future in as_completed(future_to_district):
                district = future_to_district[future]
                try:
                    journey_duration = future.result()
                    logging.info(f"Journey to {district} took {journey_duration} minutes")
                    print(f"    Journey to {district} took {journey_duration} minutes")
                    if journey_duration <= max_travel_time:
                        result_districts[district] = journey_duration
                except Exception as e:
                    logging.error(f"Error calculating journey to {district}: {str(e)}")
        
        print(time.time() - start_time)      
        return result_districts
    
    # If cache is provided, use the original approach
    for (district, data) in filtered_districts_dict.items():
        # workplace district should compute from center of district
        if district == workplace_district:
            journey_duration = get_journey(workplace_latitude, workplace_longitude, data['latitude'], data['longitude'])
            if journey_duration <= max_travel_time:
                result_districts[district] = journey_duration
            continue

        journey_duration = travel_cache.get((workplace_district, district))

        if journey_duration is None: # should never happen
            journey_duration = get_journey(districts[workplace_district]['latitude'], districts[workplace_district]['longitude'], data['latitude'], data['longitude'])
        
        if journey_duration <= max_travel_time:
            result_districts[district] = journey_duration

    
    return result_districts

def get_all_distances(districts):
    distances = {}
    logging.info("Caching all distances...")
    
    # Calculate total number of distance calculations needed
    n = (len(districts) * (len(districts)-1) // 2)  # Only one-way journeys
    i = 0
    
    # Create a list of all district pairs we need to calculate
    # Only calculate one-way journeys, using alphabetical ordering to ensure consistency
    district_pairs = []
    district_names = sorted(districts.keys())  # Sort districts alphabetically
    
    for i, district1 in enumerate(district_names):
        for district2 in district_names[i+1:]:  # Only consider districts that come after district1
            district_pairs.append((district1, district2))
    
    logging.info(f"Will calculate {len(district_pairs)} one-way journeys between districts")
    
    # Rate limiting variables
    request_timestamps = []
    requests_per_minute_limit = 499  # To be safe, staying below 500
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        # Map of futures to their district pairs
        future_to_pair = {}
        
        for district1, district2 in district_pairs:
            # Check rate limiting
            current_time = time.time()
            request_timestamps = [t for t in request_timestamps if current_time - t < 60]  # Keep only timestamps from last minute
            
            if len(request_timestamps) >= requests_per_minute_limit:
                # Sleep until we're under the rate limit
                oldest_timestamp = min(request_timestamps)
                sleep_time = 60 - (current_time - oldest_timestamp)
                if sleep_time > 0:
                    logging.info(f"Rate limit approaching, sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
                    # Reset timestamps after sleeping
                    current_time = time.time()
                    request_timestamps = []
            
            # Add current request timestamp
            request_timestamps.append(current_time)
            
            # Submit job to executor
            future = executor.submit(
                get_journey,
                districts[district1]['latitude'],
                districts[district1]['longitude'],
                districts[district2]['latitude'],
                districts[district2]['longitude']
            )
            future_to_pair[future] = (district1, district2)
            
            if len(future_to_pair) % 10 == 0:
                logging.info(f"Submitted: {len(future_to_pair)}/{len(district_pairs)} ({len(future_to_pair)/len(district_pairs)*100:.2f}%)")
        
        # Process completed futures
        completed = 0
        for future in as_completed(future_to_pair):
            district1, district2 = future_to_pair[future]
            try:
                journey_duration = future.result()
                # Store both directions with the same journey duration
                distances[(district1, district2)] = journey_duration
                distances[(district2, district1)] = journey_duration  # Assume return journey takes the same time
                
                completed += 1
                if completed % 10 == 0:
                    logging.info(f"Completed: {completed}/{len(district_pairs)} ({completed/len(district_pairs)*100:.2f}%)")
            except Exception as e:
                logging.error(f"Error calculating journey from {district1} to {district2}: {str(e)}")

    logging.info("All distances cached")
    return distances


def get_journey(from_lat, from_lon, to_lat, to_lon):
    """
    Get the average journey time in minutes for public transport duration from one location to another, without the walking time
    """

    output = "applications/json"
    r = requests.get(f'https://api.tfl.gov.uk/Journey/JourneyResults/{from_lat},{from_lon}/to/{to_lat},{to_lon}?nationalSearch=false&date=20250224&time=0900&timeIs=Arriving&journeyPreference=LeastWalking&alternativeCycle=false&walkingOptimization=true&routeBetweenEntrances=false&app_id=Burghandi&app_key=95598b12d85e401fbe896c199885b792', 
                     headers={'Accept': output})
    if (r.status_code!=200):
        raise Exception(f'Failed to get journey: from {from_lat},{from_lon} to {to_lat},{to_lon} with status code {r.status_code}')
    
    journeys = r.json()['journeys']
    if len(journeys) < 1:
        raise Exception(f'No journey found: from {from_lat},{from_lon} to {to_lat},{to_lon}')
    
    if journeys[0] == "walking":
        journeys = journeys[1:]
    journey_duration = [journey['duration'] for journey in journeys]

    return round(sum(journey_duration)/len(journey_duration))


if __name__ == "__main__":
    districts = pickle.load(open('districts.pkl', 'rb'))
    print(filter_districts_by_distance("BR1", 51.41204637320559,0.0209232400318979, districts, 30))

