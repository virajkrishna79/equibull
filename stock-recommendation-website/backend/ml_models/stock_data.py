# stock_data.py
"""
Fixed stock data for screening - avoids API rate limiting
"""

STOCK_DATA = {
    "MONARCH": {"price": 462.85, "mcap": 1006.05, "volume": 57.22},
    "HINDZINC": {"price": 476.50, "mcap": 201336.45, "volume": 11.58},
    "COALINDIA": {"price": 388.65, "mcap": 239514.44, "volume": 4262.64},
    "CANARABANK": {"price": 316.85, "mcap": 6318.54, "volume": 48.71},
    "BONDADA": {"price": 447.55, "mcap": 4994.37, "volume": 92.56},
    "BEL": {"price": 426.10, "mcap": 311469.68, "volume": 1287.16},
    "ITC": {"price": 420.35, "mcap": 526607.66, "volume": 5186.55},
    "SHREEJI": {"price": 266.47, "mcap": 4341.28, "volume": 42.70},
    "STEELCAST": {"price": 224.90, "mcap": 2275.99, "volume": 23.21},
    "GARUDA": {"price": 216.64, "mcap": 2015.66, "volume": 27.14},
    "NMDC": {"price": 75.79, "mcap": 66633.19, "volume": 1698.04},
    "INDUSTOWERS": {"price": 363.60, "mcap": 97987.91, "volume": 1839.30},
    "JAINRES": {"price": 386.05, "mcap": 13322.04, "volume": 98.64},
    "VEDANTA": {"price": 493.55, "mcap": 192997.20, "volume": 3479.00},
    "VARUNBEV": {"price": 1450.00, "mcap": 195000.00, "volume": 1200.00}
}

# Map to yfinance symbols (for when APIs work)
YF_SYMBOLS = {
    "MONARCH": "MONARCH.NS",
    "HINDZINC": "HINDZINC.NS", 
    "COALINDIA": "COALINDIA.NS",
    "CANARABANK": "CANBK.NS",
    "BONDADA": "BONDADA.NS",
    "BEL": "BEL.NS",
    "ITC": "ITC.NS",
    "SHREEJI": "SHREEJI.NS",
    "STEELCAST": "STEELCAST.NS",
    "GARUDA": "GARUDA.NS",
    "NMDC": "NMDC.NS",
    "INDUSTOWERS": "INDUSTOWER.NS",
    "JAINRES": "JAINRES.NS",
    "VEDANTA": "VEDL.NS",
    "VARUNBEV": "VBL.NS"
}

def get_stock_data():
    """Return the fixed stock data"""
    return STOCK_DATA

def get_yf_symbols():
    """Return the yfinance symbol mapping"""
    return YF_SYMBOLS

def get_stock_list():
    """Return list of stock symbols"""
    return list(STOCK_DATA.keys())
