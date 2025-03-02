import yfinance as yf
import pandas as pd
import numpy as np
import statsmodels.api as sm
from datetime import datetime, timedelta

# For FRED API integration
from fredapi import Fred

# -----------------------------------------------------------------------------
# Data Integration Functions using Free Sources
# -----------------------------------------------------------------------------
def get_gas_historical_data(start_date='2010-01-01'):
    """
    Retrieve historical natural gas price data from Yahoo Finance.
    Uses ticker 'NG=F'. Returns a DataFrame with columns 'Date' and 'Price'.
    """
    ticker = 'NG=F'
    data = yf.download(ticker, start=start_date)
    df = data.reset_index()[['Date', 'Close']]
    df.rename(columns={'Close': 'Price'}, inplace=True)
    return df

def get_gas_futures_data():
    """
    Simulate gas futures contracts data based on the latest historical price.
    Note: Detailed gas futures contracts data are typically not available for free.
    Returns a DataFrame with columns 'expiry_date' and 'price'.
    """
    hist = get_gas_historical_data()
    # Extract the numeric value directly from the Series
    latest_price_series = hist['Price'].iloc[-1]
    
    # Extract the numeric value using one of these approaches
    if isinstance(latest_price_series, pd.Series):
        # If it's still a Series, extract the value
        latest_price = latest_price_series.iloc[0] if len(latest_price_series) > 0 else float(latest_price_series)
    else:
        # If it's already a scalar value
        latest_price = float(latest_price_series)
    
    print("Latest price (converted to float):", latest_price)
    
    # Generate simulated futures contracts for the next 10 years.
    future_dates = pd.date_range(start=datetime.today(), periods=10, freq='YE')
    futures_df = pd.DataFrame({
        'expiry_date': future_dates,
        'price': latest_price * (1 + np.linspace(0.01, 0.10, 10))
    })
    return futures_df

def get_electricity_historical_data(start_date='2010-01-01', fred_api_key='your_fred_api_key'):
    """
    Retrieve historical electricity price data from FRED.
    Replace 'ELEC.PRICE' with an appropriate series ID if needed.
    Returns a DataFrame with columns 'Date' and 'Price'.
    """
    try:
        fred = Fred(api_key=fred_api_key)
        series_id = 'ELEC.PRICE'  # Replace with correct series ID if necessary
        data = fred.get_series(series_id, observation_start=start_date)
        df = data.reset_index()
        df.columns = ['Date', 'Price']
        df['Date'] = pd.to_datetime(df['Date'])
        return df
    except Exception as e:
        print("Error retrieving electricity data from FRED:", e)
        # Fallback: simulate data if FRED fails.
        dates = pd.date_range(start=start_date, periods=120, freq='M')
        prices = np.random.uniform(30, 50, len(dates))
        return pd.DataFrame({'Date': dates, 'Price': prices})

def get_electricity_futures_data():
    """
    Simulate electricity futures contracts data based on the latest historical price.
    Returns a DataFrame with columns 'expiry_date' and 'price'.
    """
    hist = get_electricity_historical_data(fred_api_key='your_fred_api_key')
    latest_price = hist['Price'].iloc[-1]
    future_dates = pd.date_range(start=datetime.today(), periods=10, freq='YE')
    futures_df = pd.DataFrame({
        'expiry_date': future_dates,
        'price': latest_price * (1 + np.linspace(0.01, 0.10, 10))
    })
    return futures_df

def get_water_historical_data(start_date='2010-01-01'):
    """
    Simulate historical water price data.
    Free direct water price data is scarce, so this function generates synthetic data.
    Returns a DataFrame with columns 'Date' and 'Price'.
    """
    dates = pd.date_range(start=start_date, periods=120, freq='M')
    prices = np.random.uniform(1, 3, len(dates))
    return pd.DataFrame({'Date': dates, 'Price': prices})

def get_water_futures_data():
    """
    Simulate water futures contracts data based on the latest historical price.
    Returns a DataFrame with columns 'expiry_date' and 'price'.
    """
    hist = get_water_historical_data()
    latest_price = hist['Price'].iloc[-1]
    future_dates = pd.date_range(start=datetime.today(), periods=10, freq='YE')
    futures_df = pd.DataFrame({
        'expiry_date': future_dates,
        'price': latest_price * (1 + np.linspace(0.01, 0.10, 10))
    })
    return futures_df

# -----------------------------------------------------------------------------
# Forecasting Functions for Bills
# -----------------------------------------------------------------------------
def forecast_commodity(historical_df, futures_df, target_year):
    # Historical Trend Forecast
    df_hist = historical_df.copy()
    df_hist['Timestamp'] = df_hist['Date'].map(datetime.timestamp)
    X = sm.add_constant(df_hist['Timestamp'])
    y = df_hist['Price']
    model = sm.OLS(y, X).fit()
    
    future_date = datetime.today() + timedelta(days=target_year * 365)
    future_timestamp = future_date.timestamp()
    # Ensure future_timestamp is 2D by reshaping it
    X_future = sm.add_constant(np.array([future_timestamp]).reshape(-1, 1))
    hist_forecast = model.predict(X_future)[0]
    
    # Futures Contracts Forecast
    futures_forecast = None
    if futures_df is not None and not futures_df.empty:
        df_fut = futures_df.copy()
        df_fut['Expiry'] = pd.to_datetime(df_fut['expiry_date'])
        df_fut['years_to_expiry'] = (df_fut['Expiry'] - pd.Timestamp.today()).dt.days / 365
        df_fut['expiry_year'] = df_fut['years_to_expiry'].round()
        df_target = df_fut[df_fut['expiry_year'] == target_year]
        if not df_target.empty:
            futures_forecast = df_target['price'].mean()
    
    # Composite Forecast: average the two if futures data is available.
    if futures_forecast is not None:
        final_forecast = (hist_forecast + futures_forecast) / 2.0
    else:
        final_forecast = hist_forecast
        
    return final_forecast

def predict_bills(bills, year):
    """
    Predict the future bills for gas, electricity, and water for a given year.
    
    Model Description:
    ------------------
    The model integrates two components:
      1. Historical Trend Forecast: Uses historical data with linear regression.
      2. Futures Contracts Forecast: Averages prices of contracts expiring in the target year.
    
    The final forecast is a composite of both methods.
    
    Parameters:
    -----------
    bills : dict
        Dictionary containing data for 'gas', 'electricity', and 'water' with keys:
          - 'historical': DataFrame with historical prices.
          - 'futures': DataFrame with futures contracts data.
    year : int
        Target forecast year (e.g., 3 for three years in the future).
        
    Returns:
    --------
    dict
        Predicted prices for each commodity.
    """
    predictions = {}
    for commodity in bills:
        hist_data = bills[commodity].get('historical')
        fut_data = bills[commodity].get('futures')
        predictions[commodity] = forecast_commodity(hist_data, fut_data, year)
    return predictions

if __name__ == "__main__":
    bills = {
        'gas': {
            'historical': get_gas_historical_data(),
            'futures': get_gas_futures_data()
        }
    }
    print(predict_bills(bills, 3))