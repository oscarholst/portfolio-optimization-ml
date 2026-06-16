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
        print("\n❌ FEL: Ingen data returnerades från Yahoo Finance.")
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
            print("⚠️ Varning: 'Adj Close' saknas, använder 'Close' istället.")
            if isinstance(data.columns, pd.MultiIndex):
                adj_close = data.xs('Close', axis=1, level=0)
            else:
                adj_close = data['Close']
        else:
            print(f"❌ Fel: Hittade varken 'Adj Close' eller 'Close'. Tillgängliga kolumner: {data.columns}")
            raise KeyError("Kunde inte extrahera prishistorik.")
            
    return adj_close.dropna(how='all')