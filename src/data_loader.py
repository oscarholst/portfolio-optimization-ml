import yfinance as yf
import pandas as pd

def download_stock_data(tickers: list, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Downloads historical adjusted closing prices with error handling.
    """
    print(f"Fetching data for {len(tickers)} assets from Yahoo Finance...")
    
    # Download data
    data = yf.download(tickers, start=start_date, end=end_date)
    
    # 1. Check whether the dataset is completely empty (network error / API timeout)
    if data.empty:
        print("\nERROR: No data was returned from Yahoo Finance.")
        print("This is usually caused by a temporary network issue or API blocking.")
        print("Check your internet connection and try running the cell again in a moment.\n")
        return pd.DataFrame()
        
    # 2. Retrieve 'Adj Close' safely (handles both flat index and MultiIndex)
    try:
        if isinstance(data.columns, pd.MultiIndex):
            adj_close = data.xs('Adj Close', axis=1, level=0)
        else:
            adj_close = data['Adj Close']
    except KeyError:
        # Fallback if Yahoo only returned regular 'Close'
        if 'Close' in data.columns:
            print("Warning: 'Adj Close' is missing, using 'Close' instead.")
            if isinstance(data.columns, pd.MultiIndex):
                adj_close = data.xs('Close', axis=1, level=0)
            else:
                adj_close = data['Close']
        else:
            print(f"Error: Found neither 'Adj Close' nor 'Close'. Available columns: {data.columns}")
            raise KeyError("Could not extract price history.")
            
    return adj_close.dropna(how='all')


def download_macro_and_market_data(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Downloads global macro, currency, commodity, and index data from Yahoo Finance.
    """
    print("Fetching global market and macro data (VIX, rates, currencies, commodities, indices)...")
    
    # Dictionary with tickers and the names we want to assign to them
    ticker_dict = {
        '^VIX': 'VIX',          # Market risk / volatility
        '^TNX': 'US10Y',        # U.S. 10-year rate
        'USDSEK=X': 'USDSEK',   # USD/SEK exchange rate
        'EURSEK=X': 'EURSEK',   # EUR/SEK exchange rate
        'HG=F': 'Copper',       # Copper price (industrial proxy)
        'BZ=F': 'Brent_Oil',    # Oil price (inflation proxy)
        '^GSPC': 'SP500',       # U.S. market
        '^OMX': 'OMXS30_Index'  # Swedish market
    }
    
    # Download data
    data = yf.download(list(ticker_dict.keys()), start=start_date, end=end_date)
    
    if data.empty:
        print("Error: Could not fetch market data.")
        return pd.DataFrame()
        
    # Extract closing prices safely
    if isinstance(data.columns, pd.MultiIndex):
        df = data.xs('Close', axis=1, level=0)
    else:
        df = data['Close']
        
    # Rename columns to clean, readable names
    df = df.rename(columns=ticker_dict)
    
    return df.dropna(how='all')