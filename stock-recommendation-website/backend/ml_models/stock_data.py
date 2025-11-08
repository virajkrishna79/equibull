"""
Fixed stock data for screening - avoids API rate limiting
"""

STOCK_DATA = {
    "GHVINFRA": {"price": 332.40, "mcap": 2395.77, "volume": 73.98},
    "INTERNATIONALGE": {"price": 360.10, "mcap": 15562.07, "volume": 76.55},
    "DAMCAPITAL": {"price": 263.22, "mcap": 1860.60, "volume": 40.00},
    "HINDZINC": {"price": 474.50, "mcap": 200491.39, "volume": 61.84},
    "SAATVIKGREEN": {"price": 490.25, "mcap": 6231.32, "volume": 75.99},
    "EUROPRATIK": {"price": 329.25, "mcap": 3364.94, "volume": 70.09},
    "CANARABANK": {"price": 318.75, "mcap": 6356.43, "volume": 75.00},
    "NATIONALALUMINIUM": {"price": 234.73, "mcap": 43111.26, "volume": 51.28},
    "TIMEXGROUP": {"price": 403.25, "mcap": 4070.81, "volume": 59.93},
    "MOTHERSONWIRING": {"price": 46.78, "mcap": 31022.91, "volume": 61.73},
    "BEL": {"price": 414.25, "mcap": 302807.59, "volume": 51.14},
    "SHREEJI": {"price": 272.05, "mcap": 4432.19, "volume": 90.00},
    "IIFLCAPITAL": {"price": 337.50, "mcap": 10483.44, "volume": 30.98},
    "SUZLON": {"price": 57.38, "mcap": 78034.30, "volume": 11.73},
    "GARUDA": {"price": 242.37, "mcap": 2255.05, "volume": 67.56},
    "INDUSTOWERS": {"price": 400.80, "mcap": 108013.07, "volume": 51.03},
    "JAINRES": {"price": 385.85, "mcap": 13315.14, "volume": 73.59},
    "SHANTIGOLD": {"price": 232.82, "mcap": 1678.54, "volume": 74.89},
    "STRINGMETAVERSE": {"price": 291.55, "mcap": 3394.58, "volume": 81.79},
    "GUJPIPAVAV": {"price": 179.60, "mcap": 8682.58, "volume": 44.01},
    "VARUNBEV": {"price": 470.20, "mcap": 159021.11, "volume": 59.44},
    "EPACK": {"price": 327.95, "mcap": 3294.32, "volume": 64.54},
    "PRIMESECURITIES": {"price": 301.70, "mcap": 1015.08, "volume": 0.00},
    "ADANIPOWER": {"price": 151.48, "mcap": 292124.56, "volume": 74.96},
    "AEROFLEX": {"price": 186.16, "mcap": 2407.43, "volume": 66.99}
}

# Map to yfinance symbols (for when APIs work)
YF_SYMBOLS = {
    "GHVINFRA": "GHVINFRA.NS",
    "INTERNATIONALGE": "INTERNATIONALGE.NS",
    "DAMCAPITAL": "DAMCAPITAL.NS",
    "HINDZINC": "HINDZINC.NS", 
    "SAATVIKGREEN": "SAATVIKGREEN.NS",
    "EUROPRATIK": "EUROPRATIK.NS",
    "CANARABANK": "CANBK.NS",
    "NATIONALALUMINIUM": "NATIONALALUM.NS",
    "TIMEXGROUP": "TIMEXGROUP.NS",
    "MOTHERSONWIRING": "MOTHERSONWIR.NS",
    "BEL": "BEL.NS",
    "SHREEJI": "SHREEJI.NS",
    "IIFLCAPITAL": "IIFLCAPITAL.NS",
    "SUZLON": "SUZLON.NS",
    "GARUDA": "GARUDA.NS",
    "INDUSTOWERS": "INDUSTOWER.NS",
    "JAINRES": "JAINRES.NS",
    "SHANTIGOLD": "SHANTIGOLD.NS",
    "STRINGMETAVERSE": "STRINGMETA.NS",
    "GUJPIPAVAV": "GUJPIPAVAV.NS",
    "VARUNBEV": "VBL.NS",
    "EPACK": "EPACK.NS",
    "PRIMESECURITIES": "PRIMESEC.NS",
    "ADANIPOWER": "ADANIPOWER.NS",
    "AEROFLEX": "AEROFLEX.NS"
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
