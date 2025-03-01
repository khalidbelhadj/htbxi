from utils import get_rent_by_district, get_postcodes_by_coordinates
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

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
        postcodes = get_postcodes_by_coordinates(latitude, longitude)
        
        if not postcodes.get('result'):
            return jsonify({
                'error': 'No postcodes found for the given coordinates'
            }), 404
            
        # Get rent data for the first postcode's district
        first_postcode = postcodes['result'][0]
        district = first_postcode['outcode']
        
        rent_data = get_rent_by_district(district)
        
        if rent_data is None or rent_data.empty:
            return jsonify({
                'error': f'No rent data found for district {district}'
            }), 404
            
        # Extract constraints from request
        min_rent = data.get('min_rent')
        max_rent = data.get('max_rent')

        # Filter rent data based on constraints
        if min_rent is not None:
            rent_data = rent_data[rent_data['Mean'] >= min_rent]
        if max_rent is not None:
            rent_data = rent_data[rent_data['Mean'] <= max_rent]

        if rent_data.empty:
            return jsonify({
                'error': 'No rent data found matching the given constraints'
            }), 404

        # get average rent value for each postcode
        rent_predictions = rent_data.groupby('Postcode')['Mean'].mean().to_dict()
        
        return jsonify({
            'district': district,
            'predictions': rent_predictions,
            'location': {
                'latitude': first_postcode.get('latitude'),
                'longitude': first_postcode.get('longitude')
            }
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)