class Markets:
    AVAILABLE_MARKETS = {
        # CRYPTO (24/7)
        "BTCUSD": {"symbol": "BTC/USD", "type": "crypto", "schedule": "24/7"},
        "ETHUSD": {"symbol": "ETH/USD", "type": "crypto", "schedule": "24/7"},
        "SOLUSD": {"symbol": "SOL/USD", "type": "crypto", "schedule": "24/7"},
        "DOGEUSD": {"symbol": "DOGE/USD", "type": "crypto", "schedule": "24/7"},
        "XRPUSD": {"symbol": "XRP/USD", "type": "crypto", "schedule": "24/7"},
        "BNBUSD": {"symbol": "BNB/USD", "type": "crypto", "schedule": "24/7"},
        "LTCUSD": {"symbol": "LTC/USD", "type": "crypto", "schedule": "24/7"},

        # FOREX (Mon-Fri, 6 AM - 11 PM MST)
        "EURUSD": {"symbol": "EUR/USD", "type": "forex", "schedule": "6:00-23:00 MST"},
        "GBPUSD": {"symbol": "GBP/USD", "type": "forex", "schedule": "6:00-23:00 MST"},
        "USDJPY": {"symbol": "USD/JPY", "type": "forex", "schedule": "6:00-23:00 MST"},
        "USDCHF": {"symbol": "USD/CHF", "type": "forex", "schedule": "6:00-23:00 MST"},
        "AUDUSD": {"symbol": "AUD/USD", "type": "forex", "schedule": "6:00-23:00 MST"},
        "USDCAD": {"symbol": "USD/CAD", "type": "forex", "schedule": "6:00-23:00 MST"},

        # U.S. STOCKS (Market Hours)
        "TSLA": {"symbol": "TSLA", "type": "stock", "schedule": "market_hours"},
        "AAPL": {"symbol": "AAPL", "type": "stock", "schedule": "market_hours"},
        "NVDA": {"symbol": "NVDA", "type": "stock", "schedule": "market_hours"},
        "META": {"symbol": "META", "type": "stock", "schedule": "market_hours"},
        "MSFT": {"symbol": "MSFT", "type": "stock", "schedule": "market_hours"},
        "AMD": {"symbol": "AMD", "type": "stock", "schedule": "market_hours"},

        # INDICES (6:30 AM - 8:30 AM MST, 12:00 PM - 1:00 PM MST)
        "SPY": {"symbol": "SPY", "type": "index", "schedule": "6:30-8:30,12:00-13:00 MST"},
        "QQQ": {"symbol": "QQQ", "type": "index", "schedule": "6:30-8:30,12:00-13:00 MST"},
        "DIA": {"symbol": "DIA", "type": "index", "schedule": "6:30-8:30,12:00-13:00 MST"},
        "IWM": {"symbol": "IWM", "type": "index", "schedule": "6:30-8:30,12:00-13:00 MST"}
    } 