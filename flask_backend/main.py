from utils import get_rent_by_district, get_postcodes_by_coordinates, get_all_districts, filter_districts_by_distance
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import pickle
import os
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# pre-load all districts
if not os.path.exists('districts.pkl'):
    districts = get_all_districts()
    pickle.dump(districts, open('districts.pkl', 'wb'))
else:
    districts = pickle.load(open('districts.pkl', 'rb'))


@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Extract coordinates from request
        workplace_latitude = data.get('workplace_latitude')
        workplace_longitude = data.get('workplace_longitude')
        
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
        filtered_districts = filter_districts_by_distance(workplace_latitude, workplace_longitude, districts, max_travel_time)
        
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

        # get average rent value for each postcode        
        return jsonify({
            'predictions': rent_data
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)