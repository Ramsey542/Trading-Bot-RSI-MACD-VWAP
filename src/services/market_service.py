from datetime import datetime, timedelta
from typing import List, Optional, Dict
from alpaca.data import StockHistoricalDataClient, CryptoHistoricalDataClient
from alpaca.data.requests import CryptoBarsRequest, StockBarsRequest
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import sys
from pathlib import Path
import pytz

root_dir = str(Path(__file__).resolve().parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from config.config import Config
from config.markets import Markets
from src.models.candle import Candle

class MarketService:
    def __init__(self):
        self.stock_client = StockHistoricalDataClient(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY)
        self.crypto_client = CryptoHistoricalDataClient(Config.ALPACA_API_KEY, Config.ALPACA_SECRET_KEY)
        self.markets = Markets.AVAILABLE_MARKETS
        self.mst = pytz.timezone('America/Denver')

    def is_market_open(self, symbol: str) -> bool:
        now = datetime.now(self.mst)
        market_info = self.markets[symbol]
        schedule = market_info["schedule"]
        market_type = market_info["type"]

        if market_type == "crypto":
            return True

        if market_type in ["forex", "stock"] and now.weekday() >= 5:
            return False

        if schedule == "market_hours":
            est = pytz.timezone('America/New_York')
            now_est = now.astimezone(est)
            market_open = now_est.replace(hour=9, minute=30, second=0, microsecond=0)
            market_close = now_est.replace(hour=16, minute=0, second=0, microsecond=0)
            return market_open <= now_est <= market_close

        elif schedule == "24/7":
            return True

        else:
            time_ranges = schedule.split(",")
            for time_range in time_ranges:
                start_str, end_str = time_range.split("-")
                start_hour, start_min = map(int, start_str.replace(" MST", "").split(":"))
                end_hour, end_min = map(int, end_str.replace(" MST", "").split(":"))
                
                market_open = now.replace(hour=start_hour, minute=start_min, second=0, microsecond=0)
                market_close = now.replace(hour=end_hour, minute=end_min, second=0, microsecond=0)
                
                if market_open <= now <= market_close:
                    return True

        return False

    def fetch_market_data(self, symbol: str, lookback_days: int = 1) -> List[Candle]:
        try:
            if not self.is_market_open(symbol):
                print(f"Market closed for {symbol}")
                return []

            symbol_info = self.markets[symbol]
            symbol_name = symbol_info["symbol"]
            market_type = symbol_info["type"]
            
            end = datetime.now()
            start = end - timedelta(days=lookback_days)
            
            timeframe = TimeFrame(amount=5, unit=TimeFrameUnit.Minute)

            if market_type == "crypto":
                request = CryptoBarsRequest(
                    symbol_or_symbols=[symbol_name],
                    timeframe=timeframe,
                    start=start,
                    end=end
                )
                bars = self.crypto_client.get_crypto_bars(request).df
            else:
                request = StockBarsRequest(
                    symbol_or_symbols=[symbol_name],
                    timeframe=timeframe,
                    start=start,
                    end=end
                )
                bars = self.stock_client.get_stock_bars(request).df
            
            candles = []
            for index, row in bars.iterrows():
                candle = Candle(
                    timestamp=index,
                    open=float(row["open"]),
                    high=float(row["high"]),
                    low=float(row["low"]),
                    close=float(row["close"]),
                    volume=float(row["volume"])
                )
                candles.append(candle)
            
            return candles
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {str(e)}")
            return [] 