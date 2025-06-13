import time
from datetime import datetime
import random
from typing import Optional, List
import sys
from pathlib import Path
import asyncio
import pytz

root_dir = str(Path(__file__).resolve().parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from config.config import Config
from config.markets import Markets
from src.services.market_service import MarketService
from src.services.telegram_service import TelegramService

from src.utils.indicators import TechnicalIndicators
from src.utils.logger import TradeLogger

class TradingBot:
    def __init__(self):
        self.market_service = MarketService()
        self.telegram_service = TelegramService()
        self.trade_logger = TradeLogger()
        self.last_trade_time: Optional[datetime] = None
        self.trade_count_today: int = 0
        self.mst = pytz.timezone('America/Denver')  
        
    def is_market_volatile(self) -> bool:
        return random.choice([True, False])
        
    def should_wait(self) -> bool:
        now = datetime.now()
        
        if self.trade_count_today >= Config.MAX_TRADES_PER_DAY:
            print("Max daily trades hit.")
            return True
            
        if self.last_trade_time and (now - self.last_trade_time).seconds < Config.COOLDOWN_MINUTES * 60:
            print("Waiting out cooldown.")
            return True
            
        return False

    def get_active_symbols(self) -> List[str]:
        active_symbols = []
        for symbol in Markets.AVAILABLE_MARKETS.keys():
            if self.market_service.is_market_open(symbol):
                active_symbols.append(symbol)
        return active_symbols
        
    async def process_symbol(self, symbol: str) -> bool:
        candles = self.market_service.fetch_market_data(symbol)
        
        if not candles:
            print(f"Skipping {symbol} due to data fetch error")
            return False
            
        score, reasons, indicator_values = TechnicalIndicators.calculate_all_indicators(candles)
        
        print(f"Score: {score}")
        print(f"Reasons: {reasons}")
        print(f"Indicators: RSI={indicator_values.get('RSI', 0):.2f}, MACD={indicator_values.get('MACD', 0):.2f}, BB={indicator_values.get('BB', 0):.2f}")
        
        if abs(score) >= Config.CONFIDENCE_THRESHOLD:
            direction = "BUY" if score > 0 else "SHORT"
            
            self.trade_logger.log_trade(symbol, direction, score, reasons, indicator_values)
            
            if self.telegram_service.is_configured():
                asyncio.create_task(
                    self.telegram_service.send_trade_alerts(symbol, direction, score, reasons)
                )
            
            self.last_trade_time = datetime.now()
            self.trade_count_today += 1
            return True
            
        return False
        
    async def run(self):
        print("Starting trading bot...")
        
        if not self.telegram_service.is_configured():
            print("Warning: Telegram bot not configured. Add TELEGRAM_TOKEN and TELEGRAM_CHAT_ID to .env file for notifications.")
        
        while True:
            if self.should_wait():
                await asyncio.sleep(30)
                continue
                
            active_symbols = self.get_active_symbols()
            
            print(f"Active symbols: {active_symbols}")
            if not active_symbols:
                print("No active markets at this time. Waiting...")
                await asyncio.sleep(60)  
                continue
                
            for symbol in active_symbols:
                await self.process_symbol(symbol)
                    
            interval = Config.CHECK_INTERVAL_VOLATILE
            print(f"Completed full scan cycle. Next scan in {interval} seconds.")
            await asyncio.sleep(interval)

if __name__ == "__main__":
    bot = TradingBot()
    asyncio.run(bot.run()) 