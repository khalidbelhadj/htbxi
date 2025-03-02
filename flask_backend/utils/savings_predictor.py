from .bills import *
from .rent_reader import get_rent_by_district, get_burrough_by_district
import yfinance as yf
from sklearn.linear_model import LinearRegression
import pandas as pd
from datetime import datetime, timedelta
import pickle
import os
import pathlib

# Create cache directory for models
def ensure_cache_dir():
    """Create cache directory if it doesn't exist"""
    cache_path = pathlib.Path(__file__).parent.resolve() / 'model_cache'
    os.makedirs(cache_path, exist_ok=True)
    return cache_path

# Function to load or train a model
def get_cached_model(model_name, train_function, force_retrain=False):
    """
    Load a model from cache or train it if not available
    
    Parameters:
    - model_name: Name of the model file
    - train_function: Function to call to train the model if not in cache
    - force_retrain: If True, retrain the model even if it exists in cache
    
    Returns:
    - The trained model
    """
    cache_path = ensure_cache_dir()
    model_path = f"{cache_path}/{model_name}.pkl"
    
    if os.path.exists(model_path) and not force_retrain:
        print(f"Loading {model_name} model from cache...")
        try:
            with open(model_path, 'rb') as f:
                model_data = pickle.load(f)
            print(f"Loaded {model_name} model from cache")
            return model_data
        except Exception as e:
            print(f"Error loading {model_name} model from cache: {e}")
            print("Will retrain model")
    
    # Train the model
    print(f"Training {model_name} model...")
    model_data = train_function()
    
    # Save the model to cache
    try:
        with open(model_path, 'wb') as f:
            pickle.dump(model_data, f)
        print(f"Saved {model_name} model to cache")
    except Exception as e:
        print(f"Error saving {model_name} model to cache: {e}")
    
    return model_data

def predict_savings(district, salary, percent_saving, sector, years, predict_cache=None):
    """
    predict for the next ten years the spending of living in this area:
    - rent - [average rent, crime rate, planning permissions, POI (schools, hospitals, etc)]
    - bills - [future price of gas, electricity, water]
    - insurance - [crime rate, Accident rate, credit swaps]
    - groceries - [POI (supermarkets)]
    - transport - [BikePoints, TODO: find other ones?]
    - inflation - [average inflation increase/decrease]

    per year, subtract from:
    - salary:
        - increase per salary progression (work sector performance)
        - your savings, according to s and p 500
    - 
    """
    if predict_cache is None:
        predict_cache = {}

    if district in predict_cache:
        return predict_cache[district]

    # Get a reasonable annual growth rate for investments
    annual_investment_rate = get_reasonable_investment_rate()
    
    wealth = 0
    investment_portfolio = 0  # Track investments separately
    predictions = [] # list of ten with a dict of predictions and reason for each year
    for year in range(years):
        stats = {}
        reasons = []
        new_salary = salary
        if year > 0:
            # Add salary progression
            new_salary = predict_salary_progression(salary, sector, year)
            wealth += new_salary
            stats['salary'] = new_salary
            reasons.append(f"This year, given you told us you work in the {sector} sector, we predict your salary will increase by {new_salary - salary}")

        # Calculate this year's savings contribution
        this_year_savings = new_salary * (percent_saving / 100)
        
        # Grow existing investment portfolio
        if investment_portfolio > 0:
            old_portfolio = investment_portfolio
            investment_portfolio *= (1 + annual_investment_rate)
            portfolio_growth = investment_portfolio - old_portfolio
            reasons.append(f"This year, your existing investments grew by £{portfolio_growth:.2f} ({annual_investment_rate*100:.1f}% return)")
            stats['investment_portfolio'] = investment_portfolio
        # Add new savings to portfolio
        investment_portfolio += this_year_savings
        reasons.append(f"This year, you saved £{this_year_savings:.2f} from your salary")
        
        # Update total wealth
        wealth = investment_portfolio
        
        # Add inflation
        wealth = predict_inflation(wealth, year, stats)
        reasons.append(f"This year, inflation adjusted your wealth to £{wealth:.2f}")
        
        # TODO: Add rent
        rent = predict_rent(district, year, stats)
        wealth -= rent
        reasons.append(f"This year, your rent payments in {district} are predicted to be £{rent:.2f}")
        stats['rent'] = rent
        
        # Add bills
        bills = {
            'gas': {
                'historical': get_gas_historical_data(),
                'futures': get_gas_futures_data(),
                'current_price': 50 * 12
            },
            'electricity': {
                'historical': get_electricity_historical_data(),
                'futures': get_electricity_futures_data(),
                'current_price': 55 * 12
            },
            'water': { 
                'historical': get_water_historical_data(),
                'futures': get_water_futures_data(),
                'current_price': 35.25 * 12
            }
        }
        bill_for_year = predict_bills(bills, year)
        for bill in bill_for_year:
            wealth -= float(bill_for_year[bill])
            reasons.append(f"This year, your {bill} bills are predicted to be {bill_for_year[bill]}")
            stats[bill] = bill_for_year[bill]

        # # TODO: Add groceries
        # groceries = predict_groceries(district, year)
        
        # Add transport
        transport = predict_transport(district, "public_transport", year, stats)
        wealth -= transport
        reasons.append(f"This year, your transport costs are predicted to be £{transport:.2f}")
        stats['transport'] = transport

        predictions.append({
            'wealth': wealth,
            'reasons': reasons,
            'stats': stats
        })
    predict_cache[district] = predictions
    return predictions


def get_reasonable_investment_rate():
    """
    Returns a reasonable annual growth rate for investments based on historical S&P 500 data.
    The long-term average annual return of the S&P 500 is about 10% before inflation,
    or about 7% after inflation.
    """
    # Get or train the investment rate model
    model_data = get_cached_model('investment_rate_model', train_investment_rate_model)
    
    if model_data is None:
        # Fallback to a reasonable default if model training failed
        print("Using default investment rate of 7%")
        return 0.07
    
    return model_data['annual_rate']


# |--------------------|
# | SALARY PROGRESSION |
# |--------------------|
def predict_salary_progression(salary, sector, year):
    """
    predict the salary progression for the next years based on sector
    """
    if sector == "Technology":
        return salary * (1 + year * 0.05)
    elif sector == "Finance":
        return salary * (1 + year * 0.03)
    elif sector == "Healthcare":
        return salary * (1 + year * 0.02)
    elif sector == "Education":
        return salary * (1 + year * 0.01)
    elif sector == "Manufacturing":
        return salary * (1 + year * 0.01)
    elif sector == "Construction":
        return salary * (1 + year * 0.01)
    elif sector == "Retail":
        return salary * (1 + year * 0.01)
    elif sector == "Other":
        return salary * (1 + year * 0.01)

# |--------------------|
# | SAVINGS            |
# |--------------------|
def get_s_and_p_500(years):
    """
    Get the S&P 500 closing prices for the last [years] years.
    """
    data = yf.Ticker("^GSPC")
    return data.history(period=f"{years}y")['Close']

def get_moving_average(s_and_p_500, window):
    """
    Calculate the moving average of the S&P 500 data over a specified window.
    """
    return s_and_p_500.rolling(window=window).mean()

def compute_annual_growth_rate(s_and_p_500, window, years):
    """
    Compute the annual growth rate based on the moving average of the S&P 500 data.
    
    Steps:
    1. Calculate the moving average.
    2. Determine the overall growth factor over the period using the first and last values.
    3. Annualize the growth factor to get the yearly growth rate.
    """
    moving_avg = get_moving_average(s_and_p_500, window).dropna()
    if len(moving_avg) < 2:
        return 0.0  # Not enough data to compute a growth rate.
    
    overall_growth = moving_avg.iloc[-1] / moving_avg.iloc[0]
    annual_rate = overall_growth**(1/years) - 1
    return annual_rate

def _predict_savings(salary, percent_saving, years, window=10):
    """
    Predict the savings after a specified number of years using the moving average
    of the S&P 500 to derive an annual growth rate.
    
    The model assumes that a lump sum equal to one year's saved amount 
    (salary * percent_saving) is invested at the start and grows over the period.
    """
    s_and_p_500 = get_s_and_p_500(years)
    annual_rate = compute_annual_growth_rate(s_and_p_500, window, years)
    # Compound the saved amount over the specified number of years:
    savings_predicted = (salary * percent_saving) * ((1 + annual_rate) ** years)
    return savings_predicted

# |--------------------|
# | INFLATION          |
# |--------------------|
def train_inflation_model():
    """Train and return the inflation prediction model and related data"""
    try:
        # Read the CSV without using the deprecated date_parser argument.
        data = pd.read_csv(
            "data/united-kingdom-inflation-rate-cpi.csv",
            skiprows=1,
            names=['Date', 'GDP Per Capita (US $)', 'Annual % Change', 'Extra'],
            usecols=[0, 1, 2]
        )
        
        # Convert the Date column to datetime using a specific format.
        data['Date'] = pd.to_datetime(data['Date'], format='%Y-%m-%d')
        data = data.dropna()
        
        # Convert dates to a numeric feature (ordinal).
        data['DateOrdinal'] = data['Date'].apply(lambda d: d.toordinal())
        
        # Fit a linear regression model using the numeric dates.
        model = LinearRegression()
        model.fit(data[['DateOrdinal']], data['Annual % Change'])
        
        # Return model and any other data needed for prediction
        return {
            'model': model,
            'training_date': datetime.now()
        }
    except Exception as e:
        print(f"Error training inflation model: {e}")
        return None

def predict_inflation(wealth, year, stats):
    """
    Predict the inflation rate for the next 'year' years.
    
    CSV format:
      Date, GDP Per Capita (US $), Annual % Change
      1961-12-31,3.4475,2.44,
      1962-12-31,4.1965,0.75,
      ...
    """
    # Get or train the inflation model
    model_data = get_cached_model('inflation_model', train_inflation_model)
    
    if model_data is None:
        # Fallback to a reasonable default if model training failed
        print("Using default inflation rate of 2%")
        return float(wealth) * (1 + 0.02)
    
    model = model_data['model']
    
    # Calculate the future date by adding the specified number of years.
    future_date = datetime.today() + timedelta(days=year * 365)
    future_date_ordinal = future_date.toordinal()
    
    # Create a DataFrame with the same column name as used for training.
    future_feature = pd.DataFrame({'DateOrdinal': [future_date_ordinal]})
    
    # Predict the inflation rate.
    prediction = model.predict(future_feature)
    
    # Ensure we're working with a scalar value, not a Series or array
    inflation_rate = float(prediction[0])
    
    # Cap inflation rate to reasonable bounds
    inflation_rate = max(min(inflation_rate, 0.10), -0.02)  # Between -2% and 10%
    stats['inflation'] = inflation_rate
    # return the new wealth as a scalar
    return float(wealth) * (1 + inflation_rate)

# |--------------------|
# | RENT               |
# |--------------------|
def train_crime_rate_model(district):
    """Train and return the crime rate prediction model for a specific district"""
    try:
        data = pd.ExcelFile("data/M1045_MonthlyCrimeDashboard_TNOCrimeData.xlsx")
        sheet = data.parse("MPS_MonthlyCrimeDashboard_TNOCr")
        
        # Get borough for the district
        burough = get_burrough_by_district(district)
        if isinstance(burough, list):
            burough = burough[0]
        
        # Filter sheet for the borough
        sheet = sheet[sheet['Area name'] == burough]
        
        if len(sheet) == 0:
            print(f"No crime data found for borough: {burough}")
            return None
            
        # Convert Month_Year to numeric for regression
        # First, ensure it's in datetime format
        if isinstance(sheet['Month_Year'].iloc[0], str):
            sheet['Month_Year'] = pd.to_datetime(sheet['Month_Year'], format='%d/%m/%Y')
        
        # Convert to ordinal for regression
        sheet['Month_Year_Ordinal'] = sheet['Month_Year'].apply(lambda x: x.toordinal())
        
        # Prepare X and y for regression
        X = sheet[['Month_Year_Ordinal']].values
        y = sheet['Count'].values
        
        # Fit regression model
        regression = LinearRegression()
        regression.fit(X, y)
        
        # Return model and metadata
        return {
            'model': regression,
            'max_count': sheet['Count'].max(),
            'borough': burough,
            'training_date': datetime.now()
        }
    except Exception as e:
        print(f"Error training crime rate model: {e}")
        return None

def get_crime_rate_penalty(district, year, stats):
    """
    get the crime rate penalty for the next years
    """
    try:
        # Get or train the crime rate model for this district
        model_data = get_cached_model(f'crime_rate_model_{district}', lambda: train_crime_rate_model(district))
        
        if model_data is None:
            return 0.0  # Default to no penalty if model training failed
        
        model = model_data['model']
        max_count = model_data['max_count']
        
        # Predict for future year
        future_date = datetime.today() + timedelta(days=365 * year)
        future_ordinal = future_date.toordinal()
        
        prediction = model.predict([[future_ordinal]])
        stats['crime_rate'] = prediction[0]
        # Normalize the prediction to get a penalty factor
        if max_count > 0:
            normalized_penalty = prediction[0] / max_count
            # Cap the penalty at a reasonable value
            return min(normalized_penalty, 0.1)  # Max 10% penalty
        else:
            return 0.0
            
    except Exception as e:
        print(f"Error calculating crime rate penalty: {e}")
        return 0.0  # Default to no penalty on error

def train_planning_permission_model(district):
    """Train and return the planning permission model for a specific district"""
    try:
        data = pd.ExcelFile("data/LDD Permissions for Datastore final.xlsx")
        sheet = data.parse("LDD data", skiprows=1, names=["Planning Authority", "Borough Reference", "Current permission status", "Permission Type", "Decision Agency", "Development Description", "Scheme Name", "Site Name/Number", "Subdivision of Building", "Primary Street Name", "Secondary Street(s)", "Post Code", "Ward", "Easting", "Northing", "Permission Date", "Permission Financial Year", "Date work commenced on site (Started Date)", "Started Financial Year", "Date construction completed (Completed Date)", "Completed Financial Year", "Date permission expires if work not commenced (Lapsed Date)", "Lapsed Financial Year", "Residential Site Area (Proposed) Hectares (ha)", "Non Res Site Area (Proposed) Hectares (ha)", "Total Open Space (Existing) Hectares (ha)", "Total Open Space (Proposed) Hectares (ha)", "Total Site Area (Proposed) Hectares (ha)", "Existing Total Residential Units", "Proposed Total Residential Units", "Proposed Total Affordable Units", "Proposed Total Affordable Percentage", "Proposed Residential Parking Spaces", "Cash in Lieu Affordable Housing", "Existing Total Bedrooms", "Proposed Total Bedrooms", "Existing Total Floorspace", "Proposed Total Floorspace"])
        
        burough = get_burrough_by_district(district)
        if isinstance(burough, list):
            burough = burough[0]
            
        # Filter sheet for the borough
        sheet = sheet[sheet['Planning Authority'] == burough]
        
        if len(sheet) == 0:
            print(f"No planning permission data found for borough: {burough}")
            return None
            
        # Clean up financial year data
        # Extract numeric part from financial year strings
        sheet['Permission Financial Year'] = sheet['Permission Financial Year'].str.replace('FY', '').astype(float)
        
        # Prepare X and y for regression
        X = sheet[['Permission Financial Year']].values
        y = sheet['Proposed Total Residential Units'].fillna(0).values
        
        # Fit regression model
        regression = LinearRegression()
        regression.fit(X, y)
        
        # Return model and metadata
        return {
            'model': regression,
            'avg_units': sheet['Proposed Total Residential Units'].mean(),
            'borough': burough,
            'training_date': datetime.now()
        }
    except Exception as e:
        print(f"Error training planning permission model: {e}")
        return None

def get_planning_permission_adjustment(district, year, stats):
    """
    get the planning permission penalty for the next years
    """
    try:
        # Get or train the planning permission model for this district
        model_data = get_cached_model(f'planning_permission_model_{district}', lambda: train_planning_permission_model(district))
        
        if model_data is None:
            return 0.0  # Default to no adjustment if model training failed
        
        model = model_data['model']
        avg_units = model_data['avg_units']
        
        # Predict for future year
        current_year = datetime.today().year
        financial_year = current_year + year
        
        prediction = model.predict([[financial_year]])
        stats['planning_permission'] = prediction[0]
        # Normalize to get an adjustment factor
        if avg_units > 0:
            # More units than average is good (increases property value)
            normalized_adjustment = (prediction[0] - avg_units) / (avg_units * 10)
            # Cap the adjustment
            return max(min(normalized_adjustment, 0.05), -0.05)  # Between -5% and +5%
        else:
            return 0.0
            
    except Exception as e:
        print(f"Error calculating planning permission adjustment: {e}")
        return 0.0  # Default to no adjustment on error

def get_poi_penalty(district, year, stats):
    """
    get the poi penalty for the next years
    """
    return 0

def predict_rent(district, year, stats):
    """
    predict the rent for the next years
    """
    try:
        # Get base rent for the district
        base_rent = float(get_rent_by_district(district))
        
        # Get adjustment factors
        crime_rate_penalty = get_crime_rate_penalty(district, year, stats)
        planning_permission_adjustment = get_planning_permission_adjustment(district, year, stats)
        poi_penalty = get_poi_penalty(district, year, stats)
        
        # Apply adjustments to base rent
        # Crime reduces rent value (negative impact)
        # Planning permissions can increase or decrease value
        # POI can affect value
        adjusted_rent = base_rent * (1 - crime_rate_penalty + planning_permission_adjustment + poi_penalty)
        
        # Apply inflation over years
        inflation_factor = 1 + (0.02 * year)  # Assume 2% annual rent inflation
        future_rent = adjusted_rent * inflation_factor
        
        return future_rent
    except Exception as e:
        print(f"Error predicting rent: {e}")
        # If there's an error, try to return just the base rent
        try:
            return float(get_rent_by_district(district))
        except:
            return 1000  # Default fallback value

# |--------------------|
# | INSURANCE          |
# |--------------------|
def predict_insurance(district, insurance, year):
    """
    predict the insurance for the next years
    """
    pass

# |--------------------|
# | GROCERIES          |
# |--------------------|
def predict_groceries(district):
    """
    predict the groceries for the next years
    """
    pass

# |--------------------|
# | TRANSPORT          |
# |--------------------|
def predict_transport(district, transport_mode, year=0, stats=None):
    """
    Predict the transport costs for the next years based on the district's travel zone.
    
    Parameters:
    - district: The London outcode (e.g., 'SW1', 'N1', etc.)
    - transport_mode: The mode of transport (currently only 'public_transport' is supported)
    - year: Years in the future (for potential fare increases)
    - stats: Dictionary to store additional statistics
    
    Returns:
    - Annual transport cost in GBP
    
    London travel zones and their monthly costs (as of 2023):
    - Zones 1-2: £171.70
    - Zones 1-3: £201.60
    - Zones 1-4: £246.60
    - Zones 1-5: £293.40
    - Zones 1-6: £347.00
    
    Single ticket cost is approximately £2.30
    """
    if stats is None:
        stats = {}
    
    # Define monthly travel card costs by zone coverage
    monthly_costs = {
        1: 171.70,  # Zones 1-2
        2: 171.70,  # Zones 1-2
        3: 201.60,  # Zones 1-3
        4: 246.60,  # Zones 1-4
        5: 293.40,  # Zones 1-5
        6: 347.00,  # Zones 1-6
        9: 400.00   # Outside London zones (estimated)
    }
    
    # Annual inflation rate for transport costs (estimated at 3%)
    annual_inflation_rate = 0.03
    
    # Map London outcodes to travel zones
    zone_mapping = {
        # Zone 1 (Central London)
        'EC1': 1, 'EC2': 1, 'EC3': 1, 'EC4': 1, 
        'WC1': 1, 'WC2': 1,
        'SW1': 1, 'W1': 1, 'SE1': 1, 'E1W': 1,
        'EC1A': 1, 'EC1M': 1, 'EC1N': 1, 'EC1P': 1, 'EC1R': 1, 'EC1V': 1, 'EC1Y': 1,
        'EC2A': 1, 'EC2M': 1, 'EC2N': 1, 'EC2P': 1, 'EC2R': 1, 'EC2V': 1, 'EC2Y': 1,
        'EC3A': 1, 'EC3M': 1, 'EC3N': 1, 'EC3P': 1, 'EC3R': 1, 'EC3V': 1,
        'EC4A': 1, 'EC4M': 1, 'EC4N': 1, 'EC4P': 1, 'EC4R': 1, 'EC4V': 1, 'EC4Y': 1,
        'WC1A': 1, 'WC1B': 1, 'WC1E': 1, 'WC1H': 1, 'WC1N': 1, 'WC1R': 1, 'WC1V': 1, 'WC1X': 1,
        'WC2A': 1, 'WC2B': 1, 'WC2E': 1, 'WC2H': 1, 'WC2N': 1, 'WC2R': 1,
        'SW1A': 1, 'SW1E': 1, 'SW1H': 1, 'SW1P': 1, 'SW1V': 1, 'SW1W': 1, 'SW1X': 1, 'SW1Y': 1,
        'W1A': 1, 'W1B': 1, 'W1C': 1, 'W1D': 1, 'W1F': 1, 'W1G': 1, 'W1H': 1, 
        'W1J': 1, 'W1K': 1, 'W1S': 1, 'W1T': 1, 'W1U': 1, 'W1W': 1,
        'SE1P': 1, 'N1P': 1, 'N1C': 1, 'NW1W': 1,
        
        # Zone 2
        'E1': 2, 'E2': 2, 'E3': 2, 'E8': 2, 'E9': 2, 'E14': 2, 'E15': 2, 'E16': 2, 'E20': 2,
        'N1': 2, 'N5': 2, 'N7': 2, 'N16': 2, 'N19': 2,
        'NW1': 2, 'NW3': 2, 'NW5': 2, 'NW6': 2, 'NW8': 2, 'NW10': 2,
        'SE5': 2, 'SE8': 2, 'SE10': 2, 'SE11': 2, 'SE13': 2, 'SE14': 2, 'SE15': 2, 'SE16': 2, 'SE17': 2,
        'SW2': 2, 'SW3': 2, 'SW4': 2, 'SW5': 2, 'SW6': 2, 'SW7': 2, 'SW8': 2, 'SW9': 2, 'SW10': 2, 'SW11': 2,
        'W2': 2, 'W3': 2, 'W4': 2, 'W6': 2, 'W8': 2, 'W9': 2, 'W10': 2, 'W11': 2, 'W12': 2, 'W14': 2,
        
        # Zone 3
        'E4': 3, 'E5': 3, 'E6': 3, 'E7': 3, 'E10': 3, 'E11': 3, 'E12': 3, 'E13': 3, 'E17': 3,
        'N2': 3, 'N4': 3, 'N6': 3, 'N8': 3, 'N10': 3, 'N15': 3, 'N17': 3, 'N18': 3, 'N22': 3,
        'NW2': 3, 'NW4': 3, 'NW9': 3, 'NW10': 3, 'NW11': 3,
        'SE2': 3, 'SE3': 3, 'SE4': 3, 'SE6': 3, 'SE7': 3, 'SE9': 3, 'SE12': 3, 'SE18': 3, 'SE19': 3, 'SE20': 3, 'SE21': 3, 'SE22': 3, 'SE23': 3, 'SE24': 3, 'SE25': 3, 'SE26': 3, 'SE27': 3,
        'SW12': 3, 'SW13': 3, 'SW15': 3, 'SW16': 3, 'SW17': 3, 'SW18': 3, 'SW19': 3, 'SW20': 3,
        'W5': 3, 'W7': 3, 'W13': 3,
        'IG1': 3, 'IG2': 3, 'IG3': 3, 'IG4': 3, 'IG5': 3, 'IG6': 3, 'IG8': 3, 'IG11': 3,
        'RM1': 3, 'RM2': 3, 'RM3': 3, 'RM5': 3, 'RM6': 3, 'RM7': 3, 'RM8': 3, 'RM9': 3, 'RM10': 3, 'RM11': 3, 'RM12': 3, 'RM13': 3,
        
        # Zone 4
        'E18': 4, 'N3': 4, 'N9': 4, 'N11': 4, 'N12': 4, 'N13': 4, 'N14': 4, 'N20': 4, 'N21': 4,
        'NW7': 4, 'NW9': 4, 'NW26': 4,
        'SE28': 4,
        'HA0': 4, 'HA1': 4, 'HA2': 4, 'HA3': 4, 'HA4': 4, 'HA5': 4, 'HA7': 4, 'HA8': 4, 'HA9': 4,
        'TW3': 4, 'TW4': 4, 'TW5': 4, 'TW7': 4, 'TW8': 4, 'TW13': 4, 'TW14': 4,
        'UB1': 4, 'UB2': 4, 'UB3': 4, 'UB4': 4, 'UB5': 4, 'UB6': 4, 'UB10': 4,
        'IG7': 4, 'IG9': 4,
        'RM4': 4, 'RM14': 4,
        
        # Zone 5
        'BR1': 5, 'BR2': 5, 'BR3': 5, 'BR4': 5, 'BR5': 5, 'BR6': 5, 'BR7': 5, 'BR8': 5,
        'CR0': 5, 'CR2': 5, 'CR3': 5, 'CR4': 5, 'CR5': 5, 'CR6': 5, 'CR7': 5, 'CR8': 5, 'CR9': 5, 'CR90': 5,
        'DA1': 5, 'DA5': 5, 'DA6': 5, 'DA7': 5, 'DA8': 5, 'DA14': 5, 'DA15': 5, 'DA16': 5, 'DA17': 5, 'DA18': 5,
        'EN1': 5, 'EN2': 5, 'EN3': 5, 'EN4': 5, 'EN5': 5,
        'HA6': 5,
        'KT1': 5, 'KT2': 5, 'KT3': 5, 'KT4': 5, 'KT5': 5, 'KT6': 5, 'KT7': 5, 'KT8': 5, 'KT9': 5,
        'SM1': 5, 'SM2': 5, 'SM3': 5, 'SM4': 5, 'SM5': 5, 'SM6': 5, 'SM7': 5,
        'TW1': 5, 'TW2': 5, 'TW6': 5, 'TW9': 5, 'TW10': 5, 'TW11': 5, 'TW12': 5,
        'UB7': 5, 'UB8': 5, 'UB9': 5, 'UB11': 5, 'UB18': 5,
        'WD6': 5, 'WD23': 5,
        
        # Zone 6
        'EN6': 6, 'EN7': 6, 'EN8': 6, 'EN9': 6,
        'HA7': 6,
        'KT17': 6, 'KT18': 6, 'KT19': 6, 'KT22': 6,
        'RM15': 6,
        'TN14': 6, 'TN16': 6,
        'TW15': 6, 'TW19': 6,
        'WD3': 6,
        
        # Outside London zones (Zone 9 for our purposes)
        'CM13': 9, 'CM14': 9, 'CM23': 9,
        'N81': 9, 'SW95': 9, 'E98': 9
    }
    
    # Extract the outcode from the district
    # For districts like 'EC1A', we need to check both 'EC1A' and 'EC1'
    zone = None
    if district in zone_mapping:
        zone = zone_mapping[district]
    else:
        # Try to extract the main outcode (e.g., 'EC1' from 'EC1A')
        main_outcode = ''.join([c for c in district if not c.isdigit()]) + ''.join([c for c in district if c.isdigit()])
        if main_outcode in zone_mapping:
            zone = zone_mapping[main_outcode]
        else:
            # If we still can't find it, try just the letter part and first digit
            letter_part = ''.join([c for c in district if not c.isdigit()])
            digit_part = ''.join([c for c in district if c.isdigit()])
            if digit_part:
                simple_outcode = letter_part + digit_part[0]
                if simple_outcode in zone_mapping:
                    zone = zone_mapping[simple_outcode]
    
    # Default to zone 6 if we can't determine the zone
    if zone is None:
        print(f"Warning: Could not determine travel zone for district {district}. Defaulting to Zone 6.")
        zone = 6
    
    # Get the monthly cost based on the zone
    monthly_cost = monthly_costs.get(zone, monthly_costs[6])  # Default to Zone 6 cost if not found
    
    # Apply inflation for future years
    inflated_monthly_cost = monthly_cost * ((1 + annual_inflation_rate) ** year)
    
    # Calculate annual cost (12 months)
    annual_cost = inflated_monthly_cost * 12
    
    # Store stats if provided
    if stats is not None:
        stats['transport_zone'] = zone
        stats['transport_monthly_cost'] = inflated_monthly_cost
        stats['transport_annual_cost'] = annual_cost
    
    return annual_cost

# |--------------------|
# | SAVINGS            |
# |--------------------|
def train_investment_rate_model():
    """Train and return the investment rate model"""
    try:
        s_and_p_500 = get_s_and_p_500(20)
        annual_rate = compute_annual_growth_rate(s_and_p_500, window=252, years=20)
        
        # Cap the rate to be within reasonable bounds
        if annual_rate > 0.10:  # Cap at 10%
            annual_rate = 0.10
        elif annual_rate < 0.04:  # Floor at 4%
            annual_rate = 0.04
        
        return {
            'annual_rate': annual_rate,
            'training_date': datetime.now()
        }
    except Exception as e:
        print(f"Error training investment rate model: {e}")
        return None


if __name__ == "__main__":
    # print(_predict_savings(100_000, 0.1, 10))
    # print(predict_inflation(100_000, 10))
    # print(get_crime_rate_penalty("BR1", 10))
    # print(get_planning_permission_adjustment("BR1", 10))
    # print(predict_rent("BR1", 10))
    # print(predict_savings("BR1", 100_000, 0.1, "Technology", 10))
    print(predict_transport("BR1", 10))