from bills import predict_bills
import yfinance as yf

def predict_savings(district, predict_cache=None):
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

    predictions = [] # list of ten with a dict of predictions and reason for each year
    
    # TODO: Add salary progression

    # TODO: Add savings increase

    # TODO: Add inflation

    # TODO: Add rent

    # TODO: Add bills

    # TODO: Add insurance

    # TODO: Add groceries
    
    # TODO: Add transport



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
def get_s_and_p_500(year):
    """
    get the s and p 500 from the last 10 years
    """
    data = yf.Ticker("^GSPC")
    return data.history(period=f"{year}y")['Close']

def get_moving_average(s_and_p_500, window):
    """
    get the moving average of the s and p 500
    """
    return s_and_p_500.rolling(window=window).mean()

def predict_s_and_p_500(year, moving_average):
    """
    predict the s and p 500 for the next [year] years
    """
    return moving_average.iloc[-1] * (1 + year * 0.05)

def _predict_savings(salary, percent_saving, year):
    """
    predict the savings for the next years based on s and p 500
    """
    # get s and p 500 from the last [year] years
    s_and_p_500 = get_s_and_p_500(year)
    # predict the s and p 500 for the next years
    s_and_p_500_predicted = predict_s_and_p_500(s_and_p_500, 10, get_moving_average(s_and_p_500, 10))
    # predict the savings for the next years
    savings_predicted = (salary * percent_saving) * s_and_p_500_predicted
    return savings_predicted

# |--------------------|
# | INFLATION          |
# |--------------------|
def predict_inflation(wealth, inflation, year):
    """
    predict the inflation for the next years
    """
    pass

# |--------------------|
# | RENT               |
# |--------------------|
def predict_rent(district, year):
    """
    predict the rent for the next years
    """
    pass

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
    print(_predict_savings(100_000, 0.1, 10))