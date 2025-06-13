import csv
from datetime import datetime
from pathlib import Path
import os

class TradeLogger:
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        self.ensure_log_directory()
        self.log_file = self.get_log_file_path()
        self.initialize_log_file()
        
    def ensure_log_directory(self):
        Path(self.log_dir).mkdir(parents=True, exist_ok=True)
        
    def get_log_file_path(self) -> str:
        today = datetime.now().strftime("%Y-%m-%d")
        return os.path.join(self.log_dir, f"trades_{today}.csv")
        
    def initialize_log_file(self):
        if not os.path.exists(self.log_file):
            with open(self.log_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(['Timestamp', 'Symbol', 'Direction', 'Score', 'Signals', 'RSI', 'MACD', 'BB'])
                
    def log_trade(self, symbol: str, direction: str, score: float, reasons: list, indicator_values: dict):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        clean_reasons = []
        for reason in reasons:
            if "RSI" in reason:
                clean_reasons.append("RSI")
            if "MACD" in reason:
                clean_reasons.append("MACD")
            if "BB" in reason:
                clean_reasons.append("BB")
            if "VWAP" in reason:
                clean_reasons.append("VWAP")
            if "VOL" in reason:
                clean_reasons.append("VOL")
            if "PA" in reason:
                clean_reasons.append("PA")
                
        reasons_str = "|".join(clean_reasons)
        
        rsi = indicator_values.get("RSI", 0)
        macd = indicator_values.get("MACD", 0)
        bb = indicator_values.get("BB", 0)
        
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                timestamp,
                symbol,
                direction,
                int(score),
                reasons_str,
                rsi,
                macd,
                bb
            ])
            
    def get_todays_trades(self) -> list:
        trades = []
        if os.path.exists(self.log_file):
            with open(self.log_file, 'r') as f:
                reader = csv.DictReader(f)
                trades = list(reader)
        return trades 