import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# List of major semiconductor companies traded on NYSE
SEMICONDUCTOR_TICKERS = [
    'AMD', 'INTC', 'NVDA', 'TSM', 'QCOM', 'TXN', 'AMAT', 'ASML', 
    'MU', 'LRCX', 'ADI', 'MCHP', 'KLAC', 'NXPI', 'ON'
]

def get_company_info(ticker):
    """Fetch company information for a given ticker."""
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return {
            'name': info.get('longName', 'N/A'),
            'sector': info.get('sector', 'N/A'),
            'industry': info.get('industry', 'N/A'),
            'description': info.get('longBusinessSummary', 'N/A'),
            'website': info.get('website', 'N/A')
        }
    except Exception as e:
        return None

def fetch_stock_data(tickers, period='1y'):
    """Fetch historical stock data for multiple tickers."""
    try:
        data = pd.DataFrame()
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)['Close']
            data[ticker] = hist
        return data
    except Exception as e:
        return None

def calculate_correlation(data):
    """Calculate correlation matrix from stock data."""
    if data is not None and not data.empty:
        return data.corr()
    return None

def get_price_changes(data):
    """Calculate price changes for each stock."""
    if data is None or data.empty:
        return None
    
    changes = {}
    for column in data.columns:
        initial_price = data[column].iloc[0]
        final_price = data[column].iloc[-1]
        percent_change = ((final_price - initial_price) / initial_price) * 100
        changes[column] = {
            'initial_price': round(initial_price, 2),
            'final_price': round(final_price, 2),
            'percent_change': round(percent_change, 2)
        }
    return changes
