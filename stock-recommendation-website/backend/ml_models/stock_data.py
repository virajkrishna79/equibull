"""
Fixed stock data for screening - avoids API rate limiting
"""

STOCK_DATA = {
    "GHVINFRA": {"price": 345.00, "mcap": 2486.59, "volume": 73.98},
    "HINDZINC": {"price": 475.60, "mcap": 200956.16, "volume": 61.84},
    "CANARABANK": {"price": 316.00, "mcap": 6301.60, "volume": 75.00},
    "BONDADA": {"price": 441.35, "mcap": 4925.19, "volume": 61.55},
    "BEL": {"price": 419.00, "mcap": 306279.73, "volume": 51.14},
    "ITC": {"price": 411.30, "mcap": 515269.94, "volume": 0.00},
    "SHREEJI": {"price": 270.95, "mcap": 4414.27, "volume": 90.00},
    "GARUDA": {"price": 232.45, "mcap": 2162.76, "volume": 67.56},
    "INDUSTOWERS": {"price": 390.50, "mcap": 105237.20, "volume": 51.03},
    "JAINRES": {"price": 377.05, "mcap": 13011.44, "volume": 73.59},
    "VARUNBEV": {"price": 470.90, "mcap": 159257.85, "volume": 59.44},
    "EPACK": {"price": 291.40, "mcap": 2927.13, "volume": 64.54},
    "ADANIPOWER": {"price": 157.75, "mcap": 304216.05, "volume": 74.96},
    "AEROFLEX": {"price": 188.10, "mcap": 2432.52, "volume": 66.99},
    "FABTECH": {"price": 236.15, "mcap": 1049.73, "volume": 68.94}
}

# Map to yfinance symbols (for when APIs work)
YF_SYMBOLS = {
    "GHVINFRA": "GHVINFRA.NS",
    "HINDZINC": "HINDZINC.NS", 
    "CANARABANK": "CANBK.NS",
    "BONDADA": "BONDADA.NS",
    "BEL": "BEL.NS",
    "ITC": "ITC.NS",
    "SHREEJI": "SHREEJI.NS",
    "GARUDA": "GARUDA.NS",
    "INDUSTOWERS": "INDUSTOWER.NS",
    "JAINRES": "JAINRES.NS",
    "VARUNBEV": "VBL.NS",
    "EPACK": "EPACK.NS",
    "ADANIPOWER": "ADANIPOWER.NS",
    "AEROFLEX": "AEROFLEX.NS",
    "FABTECH": "FABTECH.NS"
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
