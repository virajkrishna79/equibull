NIFTY50_SYMBOLS = [
    "RELIANCE", "TCS", "HDFCBANK", "ICICIBANK", "INFY", "ITC", "LT",
    "SBIN", "BHARTIARTL", "AXISBANK", "HINDUNILVR", "BAJFINANCE",
    "KOTAKBANK", "ASIANPAINT", "MARUTI", "SUNPHARMA", "TITAN",
    "ULTRACEMCO", "WIPRO", "NESTLEIND", "POWERGRID", "TATASTEEL",
    "ONGC", "M&M", "NTPC", "JSWSTEEL", "ADANIENT", "ADANIPORTS",
    "GRASIM", "HCLTECH", "HDFCLIFE", "TECHM", "COALINDIA", "BPCL",
    "BRITANNIA", "BAJAJFINSV", "IOC", "HEROMOTOCO", "LTIM", "CIPLA",
    "TATAMOTORS", "DRREDDY", "DIVISLAB", "EICHERMOT", "SHREECEM",
    "UPL", "SBILIFE", "TATACONSUM", "INDUSINDBK", "APOLLOHOSP"
]

def load_symbol_universe() -> list:
    """Load NSE symbol universe from data/nse_symbols.txt if present, else fallback to NIFTY50."""
    import os
    symbols_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'nse_symbols.txt')
    if os.path.exists(symbols_path):
        try:
            with open(symbols_path, 'r', encoding='utf-8') as f:
                symbols = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            # Deduplicate and sanitize
            symbols = sorted(set(sym.upper().replace('.NS', '').replace('.BO', '')) for sym in symbols)
            return symbols
        except Exception:
            return NIFTY50_SYMBOLS
    return NIFTY50_SYMBOLS


