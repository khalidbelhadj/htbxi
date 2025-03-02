import numpy as np
from sklearn.neighbors import KDTree
from utils import *
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import pickle
import os
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

global districts
global travel_cache
global tom_tom
global savings_cache

@app.route('/predict', methods=['POST'])
def predict():
    # try:
        data = request.get_json()
        
        # Extract coordinates from request to district
        workplace_latitude = data.get('latitude')
        workplace_longitude = data.get('longitude')
        workplace_district = get_district_from_coords(workplace_latitude, workplace_longitude)
        
        if not workplace_latitude or not workplace_longitude:
            return jsonify({
                'error': 'Missing required parameters: latitude and longitude'
            }), 400
        
        if not districts:
            return jsonify({
                'error': 'District data not found'
            }), 404
        
        # filter districts by distance
        max_travel_time = data.get('max_travel_time')
        transport_mode = data.get('transport_mode')

        if transport_mode == 'public_transport':
            filtered_districts = filter_districts_by_distance(workplace_district, workplace_latitude, workplace_longitude, districts, max_travel_time)
        # elif transport_mode == 'car':
        #     filtered_districts = drive_tom_tom.filter_districts_within_time(workplace_district, districts, max_travel_time)
        # elif transport_mode == 'bike':
        #     filtered_districts = bike_tom_tom.filter_districts_within_time(workplace_district, districts, max_travel_time)
        else:
            raise Exception(f"Invalid transport mode: {transport_mode}")
        
        rent_data = {}
        # Get rent data for each postcode
        for district in filtered_districts:
            rent = get_rent_by_district(district)
            rent_data[district] = rent

        logging.info(f"Rent data: {rent_data}")
        
        if rent_data is None or len(rent_data) == 0:
            return jsonify({
                'error': f'No rent data found for district {district}'
            }), 404
            
        # Extract constraints from request
        min_rent = int(data.get('min_rent'))
        max_rent = int(data.get('max_rent'))

        # Filter rent data based on constraints
        rent_data = {k: v for k, v in rent_data.items() if min_rent <= v <= max_rent}
        logging.info(f"Filtered rent data: {rent_data}")

        if len(rent_data) == 0:
            return jsonify({
                'error': 'No rent data found matching the given constraints'
            }), 404
        
        # get savings predictions for each postcode
        salary = data.get('salary')
        percent_saving = data.get('percent_saving')
        sector = data.get('sector')
        years = data.get('years')
        predictions = {}
        for district in rent_data:
            logging.info(f"Predicting savings for district: {district}")
            savings_prediction = predict_savings(district, salary, percent_saving, sector, years, predict_cache=savings_cache)
            predictions[district] = savings_prediction

        # get average rent value for each postcode        
        return jsonify({
            'recommendations': rent_data,
            'savings_predictions': predictions
        })
        
    # except Exception as e:
    #     # save caches
    #     pickle.dump(districts, open('districts.pkl', 'wb'))
    #     # pickle.dump(travel_cache, open('travel_cache.pkl', 'wb'))
    #     pickle.dump(savings_cache, open('savings_cache.pkl', 'wb'))
    #     return jsonify({
    #         'error': str(e)
    #     }), 500

if __name__ == '__main__':
    # pre-load all districts
    if not os.path.exists('districts.pkl'):
        logging.info("Districts data not found, loading from API")
        districts = get_all_districts(get_district_names())
        pickle.dump(districts, open('districts.pkl', 'wb'))
    else:
        logging.info("Districts data found, loading from file")
        districts = pickle.load(open('districts.pkl', 'rb'))
    logging.info(f"Loaded {len(districts)} districts")

    # pre-load savings cache
    if not os.path.exists('savings_cache.pkl'):
        logging.info("Savings cache not found, initialising")
        savings_cache = {}
    else:
        logging.info("Savings cache found, loading from file")
        savings_cache = pickle.load(open('savings_cache.pkl', 'rb'))
    logging.info(f"Loaded {len(savings_cache)} savings cache entries")

    # logging.info("Initialising TomTom")
    # walk_tom_tom = TomTom()
    # drive_tom_tom = TomTom(mode='drive')
    # bike_tom_tom = TomTom(mode='bike')
    # logging.info("TomTom initialised")

    # pre-load travel cache
    # if not os.path.exists('travel_cache.pkl'):
    #     logging.info("Travel cache not found, initialising")
    #     travel_cache = get_all_distances(districts)
    # else:
    #     logging.info("Travel cache found, loading from file")
    #     travel_cache = pickle.load(open('travel_cache.pkl', 'rb'))
    # logging.info(f"Loaded {len(travel_cache)} travel cache entries")
    # if not os.path.exists('travel_cache.pkl'):
    #     logging.info("Travel cache not found, initialising")
    #     travel_cache = get_all_distances(districts)
    # else:
    #     logging.info("Travel cache found, loading from file")
    #     travel_cache = pickle.load(open('travel_cache.pkl', 'rb'))
    # logging.info(f"Loaded {len(travel_cache)} travel cache entries")

    try:
        app.run(debug=True)
    except KeyboardInterrupt:
        # save caches
        pickle.dump(districts, open('districts.pkl', 'wb'))
        # pickle.dump(travel_cache, open('travel_cache.pkl', 'wb'))
        pickle.dump(savings_cache, open('savings_cache.pkl', 'wb'))
        logging.info("Caches saved")
