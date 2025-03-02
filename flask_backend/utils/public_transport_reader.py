# santos will put code here
import requests
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

def filter_districts_by_distance(workplace_district, workplace_latitude, workplace_longitude, districts, max_travel_time, travel_cache):
    filtered_districts = {}
    for (district, data) in districts.items():
        # workplace district should compute from center of district
        if district == workplace_district:
            journey_duration = get_journey(workplace_latitude, workplace_longitude, data['latitude'], data['longitude'])
            if journey_duration <= max_travel_time:
                filtered_districts[district] = journey_duration
            continue

        journey_duration = travel_cache.get((workplace_district, district))

        if journey_duration is None: # should never happen
            journey_duration = get_journey(districts[workplace_district]['latitude'], districts[workplace_district]['longitude'], data['latitude'], data['longitude'])
        
        if journey_duration <= max_travel_time:
            filtered_districts[district] = journey_duration

    return filtered_districts

def get_all_distances(districts):
    distances = {}
    logging.info("Caching all distances...")
    n = (len(districts) * (len(districts)-1)  // 2)
    i = 0

    futures = []
    for district1 in districts:
        with ThreadPoolExecutor(max_workers=10) as executor:
            for district2 in districts:
                if district1 != district2 and (district1, district2) not in distances and (district2, district1) not in distances:
                    distances[(district1, district2)] = executor.submit(get_journey, districts[district1]['latitude'], districts[district1]['longitude'], districts[district2]['latitude'], districts[district2]['longitude'])
                i += 1
                logging.info(f"Progress: {i/n*100:.2f}%")

    for result in as_completed(futures):
        district1, district2 = result.

        for district2 in districts:
            if district1 != district2 and (district1, district2) not in distances and (district2, district1) not in distances:
                distances[(district1, district2)] = get_journey(districts[district1]['latitude'], districts[district1]['longitude'], districts[district2]['latitude'], districts[district2]['longitude'])
            i += 1
            logging.info(f"Progress: {i/n*100:.2f}%")

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
    print(get_journey(51.509372,-0.076177, 51.501105,-0.126124))

