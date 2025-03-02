from .bills import *
from .rent_reader import get_rent_by_district, get_burrough_by_district
import yfinance as yf
from sklearn.linear_model import LinearRegression
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

    wealth = salary
    predictions = [] # list of ten with a dict of predictions and reason for each year
    for year in range(years):
        reasons = []
        # Add salary progression
        new_salary = predict_salary_progression(salary, sector, year)
        wealth += new_salary
        reasons.append(f"This year, given you told us you work in the {sector} sector, we predict your salary will increase by {new_salary - salary}")

        # Add savings increase
        wealth += _predict_savings(new_salary, percent_saving, year)
        reasons.append(f"This year, the S and P is expected to adjust your wealth by {wealth - salary}")
        
        # Add inflation
        wealth = predict_inflation(wealth, year)
        reasons.append(f"This year, the inflation is expected to adjust your wealth by {wealth - salary}")
        
        # TODO: Add rent
        rent = predict_rent(district, year)
        wealth -= rent
        reasons.append(f"This year, your rent payments in {district} are predicted to be {rent}")

        # Add bills
        bills = {
            'gas': {
                'historical': get_gas_historical_data(),
                'futures': get_gas_futures_data(),
                'current_price': 50
            },
            'electricity': {
                'historical': get_electricity_historical_data(),
                'futures': get_electricity_futures_data(),
                'current_price': 55
            },
            'water': { 
                'historical': get_water_historical_data(),
                'futures': get_water_futures_data(),
                'current_price': 35.25
            }
        }
        bill_for_year = predict_bills(bills, year)
        for bill in bill_for_year:
            wealth -= bill_for_year[bill]
            reasons.append(f"This year, your {bill} bills are predicted to be {bill_for_year[bill]}")
        
        # # TODO:Add insurance
        # insurance = predict_insurance(district, insurance, year)
        # wealth -= insurance
        # reasons.append(f"This year, your car insurance is predicted to be {insurance}")

        # # TODO: Add groceries
        # groceries = predict_groceries(district, year)
        
        # # TODO: Add transport
        # transport = predict_transport(district, transport, year)
        predictions.append({
            'wealth': wealth,
            'reasons': reasons
        })
    return predictions





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
    
    The model assumes that a lump sum equal to one year’s saved amount 
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
def predict_inflation(wealth, year):
    """
    Predict the inflation rate for the next 'year' years.
    
    CSV format:
      Date, GDP Per Capita (US $), Annual % Change
      1961-12-31,3.4475,2.44,
      1962-12-31,4.1965,0.75,
      ...
    """
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
    
    # Calculate the future date by adding the specified number of years.
    future_date = datetime.today() + timedelta(days=year * 365)
    future_date_ordinal = future_date.toordinal()
    
    # Create a DataFrame with the same column name as used for training.
    future_feature = pd.DataFrame({'DateOrdinal': [future_date_ordinal]})
    
    # Predict the inflation rate.
    prediction = model.predict(future_feature)
    
    # return the new wealth
    return wealth * (1 + prediction[0])

# |--------------------|
# | RENT               |
# |--------------------|
def get_crime_rate_penalty(district, year):
    """
    get the crime rate penalty for the next years
    """
    data = pd.ExcelFile("data/M1045_MonthlyCrimeDashboard_TNOCrimeData.xlsx")
    sheet = data.parse("MPS_MonthlyCrimeDashboard_TNOCr")
    """
    Format:
    Month_Year	Area Type	Borough_SNT	Area name	Area code	Offence Group	Offence Subgroup	Measure	Financial Year	FY_FYIndex	Count	Refresh Date
    01/02/2021	Borough	Barking and Dagenham	Barking and Dagenham	E09000002	ARSON AND CRIMINAL DAMAGE	ARSON	Offences	fy20-21	20-21_01	6	05/02/2025
    """
    # do regression on the crime rate to predict the crime rate for this year
    burough = get_burrough_by_district(district)
    burough = burough[0]
    sheet = sheet[sheet['Area name'] == burough]
    regression = LinearRegression()
    regression.fit(sheet['Month_Year'], sheet['Count'])
    prediction = regression.predict([[year]])
    return prediction[0]


def get_planning_permission_adjustment(district, year):
    """
    get the planning permission penalty for the next years
    """
    data = pd.ExcelFile("data/LDD Permissions for Datastore final.xlsx")
    sheet = data.parse("LDD data")
    """
    Planning Authority	Borough Reference	Current permission status	Permission Type	Decision Agency	Development Description	Scheme Name	Site Name/Number	Subdivision of Building	Primary Street Name	Secondary Street(s)	Post Code	Ward	Easting	Northing	Permission Date	Permission Financial Year	Date work commenced on site (Started Date)	Started Financial Year	Date construction completed (Completed Date)	Completed Financial Year	Date permission expires if work not commenced (Lapsed Date)	Lapsed Financial Year	Residential Site Area (Proposed) Hectares (ha)	Non Res Site Area (Proposed) Hectares (ha)	Total Open Space (Existing) Hectares (ha)	Total Open Space (Proposed) Hectares (ha)	Total Site Area (Proposed) Hectares (ha)	Existing Total Residential Units	Proposed Total Residential Units	Proposed Total Affordable Units	Proposed Total Affordable Percentage	Proposed Residential Parking Spaces	Cash in Lieu Affordable Housing	Existing Total Bedrooms	Proposed Total Bedrooms	Existing Total Floorspace	Proposed Total Floorspace
    Barking and Dagenham	00/00066/FUL	Completed	Full	Borough	Conversion of office/storage accommodation into 2 one bedroom flats		Building To Rear Of  83		Longbridge Road		IG11 8TG	ABBEY	544598	184575	06/09/2000	FY2000	24/03/2005	FY2004	15/03/2007	FY2006	06/09/2005	FY2005	0.005	0.000	0.000	0.000	0.005		2		0	2		0	0	100	0
    """
    burough = get_burrough_by_district(district)
    if burough is type(list):
        burough = burough[0]
    sheet = sheet[sheet['Planning Authority'] == burough]
    # change years to drop FY
    sheet['Permission Financial Year'] = sheet['Permission Financial Year'].apply(lambda x: x.split('FY')[1])
    sheet['Started Financial Year'] = sheet['Started Financial Year'].apply(lambda x: x.split('FY')[1])
    sheet['Completed Financial Year'] = sheet['Completed Financial Year'].apply(lambda x: x.split('FY')[1])

    regression = LinearRegression()
    # predict the number of residential units planned in [year] years
    regression.fit(sheet['Permission Financial Year'], sheet['Proposed Total Residential Units'])
    prediction = regression.predict([[year]])
    return prediction[0]

def get_poi_penalty(district, year):
    """
    get the poi penalty for the next years
    """
    return 0

def predict_rent(district, year):
    """
    predict the rent for the next years
    """
    base_rent = get_rent_by_district(district)
    return base_rent
    crime_rate_penalty = get_crime_rate_penalty(district, year)
    planning_permission_adjustment = get_planning_permission_adjustment(district, year)
    poi_penalty = get_poi_penalty(district, year)
    return base_rent * (1 + crime_rate_penalty + planning_permission_adjustment + poi_penalty)

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
def predict_transport(district, transport):
    """
    predict the transport for the next years
    """
    pass


if __name__ == "__main__":
    # print(_predict_savings(100_000, 0.1, 10))
    # print(predict_inflation(100_000, 10))
    # print(get_crime_rate_penalty("BR1", 10))
    # print(get_planning_permission_penalty("BR1", 10))
    # print(predict_rent("BR1", 10))
    print(predict_savings("BR1", 100_000, 0.1, "Technology", 10))