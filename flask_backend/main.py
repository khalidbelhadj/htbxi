from utils import get_rent_by_district, get_postcodes_by_coordinates
from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
app = Flask(__name__)
CORS(app)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@app.route('/predict', methods=['POST'])
def predict():
    try:
        data = request.get_json()
        
        # Extract coordinates from request
        latitude = data.get('latitude')
        longitude = data.get('longitude')
        
        if not latitude or not longitude:
            return jsonify({
                'error': 'Missing required parameters: latitude and longitude'
            }), 400
            
        # Get nearby postcodes
        postcodes = get_postcodes_by_coordinates(latitude, longitude, radius=10000)
        
        if not postcodes.get('result'):
            return jsonify({
                'error': 'No postcodes found for the given coordinates'
            }), 404
        
        rent_data = {}
        # Get rent data for each postcode
        for postcode in postcodes['result']:
            district = postcode['outcode']
            rent = get_rent_by_district(district)
            rent_data[postcode['outcode']] = rent

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