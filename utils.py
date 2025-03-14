import yfinance as yf
import pandas as pd
import numpy as np
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
            'website': info.get('website', 'N/A'),
            'market_cap': info.get('marketCap', 'N/A'),
            'pe_ratio': info.get('trailingPE', 'N/A'),
            'dividend_yield': info.get('dividendYield', 'N/A'),
        }
    except Exception as e:
        return None

def fetch_stock_data(tickers, period='1y'):
    """Fetch historical stock data for multiple tickers."""
    try:
        data = pd.DataFrame()
        volume_data = pd.DataFrame()
        for ticker in tickers:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)
            data[ticker] = hist['Close']
            volume_data[ticker] = hist['Volume']
        return data, volume_data
    except Exception as e:
        return None, None

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

def calculate_technical_indicators(data):
    """Calculate technical indicators for the stocks."""
    if data is None or data.empty:
        return None

    indicators = {}
    for column in data.columns:
        series = data[column]
        # Calculate 20-day moving average
        ma20 = series.rolling(window=20).mean()
        # Calculate 50-day moving average
        ma50 = series.rolling(window=50).mean()
        # Calculate RSI
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        indicators[column] = {
            'MA20': ma20.iloc[-1],
            'MA50': ma50.iloc[-1],
            'RSI': rsi.iloc[-1]
        }
    return indicators

def normalize_data(data):
    """Normalize stock prices for comparison."""
    if data is None or data.empty:
        return None

    normalized = pd.DataFrame()
    for column in data.columns:
        normalized[column] = data[column] / data[column].iloc[0] * 100
    return normalized