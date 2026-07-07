import yfinance as yf
import pandas as pd

def download_stock_data(tickers: list, start_date: str, end_date: str) -> pd.DataFrame:
    """
    Laddar ner historiska justerade stängningskurser med felhantering.
    """
    print(f"Hämtar data för {len(tickers)} tillgångar från Yahoo Finance...")
    
    # Ladda ner data
    data = yf.download(tickers, start=start_date, end=end_date)
    
    # 1. Kontrollera om datan är helt tom (Nätverksfel / API-timeout)
    if data.empty:
        print("\n FEL: Ingen data returnerades från Yahoo Finance.")
        print("Detta beror oftast på en tillfällig nätverksstörning eller API-blockering.")
        print("Kontrollera din internetanslutning och testa att köra cellen igen om en kort stund.\n")
        return pd.DataFrame()
        
    # 2. Hämta 'Adj Close' säkert (hanterar både platt index och MultiIndex)
    try:
        if isinstance(data.columns, pd.MultiIndex):
            adj_close = data.xs('Adj Close', axis=1, level=0)
        else:
            adj_close = data['Adj Close']
    except KeyError:
        # Fallback om Yahoo bara skickade med vanlig 'Close'
        if 'Close' in data.columns:
            print(" Varning: 'Adj Close' saknas, använder 'Close' istället.")
            if isinstance(data.columns, pd.MultiIndex):
                adj_close = data.xs('Close', axis=1, level=0)
            else:
                adj_close = data['Close']
        else:
            print(f" Fel: Hittade varken 'Adj Close' eller 'Close'. Tillgängliga kolumner: {data.columns}")
            raise KeyError("Kunde inte extrahera prishistorik.")
            
    return adj_close.dropna(how='all')


def download_macro_and_market_data(start_date: str, end_date: str) -> pd.DataFrame:
    """
    Laddar ner global makro-, valuta-, råvaru- och indexdata från Yahoo Finance.
    """
    print("Hämtar global marknads- och makrodata (VIX, Räntor, Valutor, Råvaror, Index)...")
    
    # Ordbok med tickers och vad vi vill döpa om dem till
    ticker_dict = {
        '^VIX': 'VIX',          # Marknadsrisk/Volatilitet
        '^TNX': 'US10Y',        # Amerikansk 10-årig ränta
        'USDSEK=X': 'USDSEK',   # Valuta USD/SEK
        'EURSEK=X': 'EURSEK',   # Valuta EUR/SEK
        'HG=F': 'Copper',       # Kopparpris (Industriproxy)
        'BZ=F': 'Brent_Oil',    # Oljepris (Inflationsproxy)
        '^GSPC': 'SP500',       # Amerikanska marknaden
        '^OMX': 'OMXS30_Index'  # Svenska marknaden
    }
    
    # Ladda ner data
    data = yf.download(list(ticker_dict.keys()), start=start_date, end=end_date)
    
    if data.empty:
        print(" Fel: Kunde inte hämta marknadsdata.")
        return pd.DataFrame()
        
    # Extrahera stängningskurser säkert
    if isinstance(data.columns, pd.MultiIndex):
        df = data.xs('Close', axis=1, level=0)
    else:
        df = data['Close']
        
    # Döp om kolumnerna till rena, begripliga namn
    df = df.rename(columns=ticker_dict)
    
    return df.dropna(how='all')