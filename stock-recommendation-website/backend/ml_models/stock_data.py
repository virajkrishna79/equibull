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
    "VARUNBEV": {"price": 1450.00, "mcap": 195000.00, "volume": 1200.00},
    # New stocks added from the list
    "RELIANCE": {"price": 1486.40, "mcap": 2011466.18, "volume": 22092.00},
    "HDFCBANK": {"price": 987.30, "mcap": 1518140.95, "volume": 20363.77},
    "BHARTIARTL": {"price": 2054.50, "mcap": 1232955.29, "volume": 7421.80},
    "TCS": {"price": 3058.00, "mcap": 1106411.16, "volume": 12131.00},
    "ICICIBANK": {"price": 1345.30, "mcap": 961306.50, "volume": 14318.15},
    "SBIN": {"price": 937.00, "mcap": 864908.87, "volume": 22121.38},
    "BAJFINANCE": {"price": 1042.80, "mcap": 648880.41, "volume": 4765.29},
    "INFY": {"price": 1482.30, "mcap": 615806.91, "volume": 7375.00},
    "HINDUNILVR": {"price": 2465.50, "mcap": 579291.73, "volume": 2694.00},
    "LICI": {"price": 894.70, "mcap": 565897.54, "volume": 10955.21},
    "LT": {"price": 4030.90, "mcap": 554482.89, "volume": 4678.01},
    "MARUTI": {"price": 16186.00, "mcap": 508892.01, "volume": 3349.00},
    "M&M": {"price": 3487.20, "mcap": 433643.37, "volume": 4376.58},
    "HCLTECH": {"price": 1541.50, "mcap": 418311.47, "volume": 4236.00},
    "KOTAKBANK": {"price": 2102.20, "mcap": 418049.82, "volume": 4468.27},
    "SUNPHARMA": {"price": 1690.70, "mcap": 405655.56, "volume": 2292.87},
    "AXISBANK": {"price": 1232.80, "mcap": 382561.82, "volume": 5566.56},
    "ULTRACEMCO": {"price": 11947.00, "mcap": 352053.21, "volume": 1237.98},
    "BAJAJFINSV": {"price": 1800.00, "mcap": 300000.00, "volume": 2500.00}  # Estimated values
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
    "VARUNBEV": "VBL.NS",
    # New symbols mapping
    "RELIANCE": "RELIANCE.NS",
    "HDFCBANK": "HDFCBANK.NS",
    "BHARTIARTL": "BHARTIARTL.NS",
    "TCS": "TCS.NS",
    "ICICIBANK": "ICICIBANK.NS",
    "SBIN": "SBIN.NS",
    "BAJFINANCE": "BAJFINANCE.NS",
    "INFY": "INFY.NS",
    "HINDUNILVR": "HINDUNILVR.NS",
    "LICI": "LICI.NS",
    "LT": "LT.NS",
    "MARUTI": "MARUTI.NS",
    "M&M": "M&M.NS",
    "HCLTECH": "HCLTECH.NS",
    "KOTAKBANK": "KOTAKBANK.NS",
    "SUNPHARMA": "SUNPHARMA.NS",
    "AXISBANK": "AXISBANK.NS",
    "ULTRACEMCO": "ULTRACEMCO.NS",
    "BAJAJFINSV": "BAJAJFINSV.NS"
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
