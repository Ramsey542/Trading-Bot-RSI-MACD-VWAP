from typing import List, Optional
import requests
from datetime import datetime
import sys
from pathlib import Path
import asyncio

root_dir = str(Path(__file__).resolve().parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from config.config import Config

class TelegramService:
    def __init__(self):
        self.token = Config.TELEGRAM_TOKEN
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}" if self.token else None
        
    def is_configured(self) -> bool:
        return bool(self.token and self.chat_id)
        
    def send_message(self, text: str, parse_mode: str = "HTML") -> bool:
        if not self.is_configured():
            print("Telegram not configured")
            return False
            
        try:
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": text,
                "parse_mode": parse_mode
            }
            response = requests.post(url, data=data)
            return response.status_code == 200
        except Exception as e:
            print(f"Error sending Telegram message: {str(e)}")
            return False
            
    def format_signal_message(self, symbol: str, direction: str, score: float, reasons: List[str]) -> str:
        emoji = "🟢" if direction == "BUY" else "🔴"
        direction_arrow = "⬆️" if direction == "BUY" else "⬇️"
        
        message = f"""
{emoji} <b>Trading Signal Alert</b> {direction_arrow}

Symbol: <code>{symbol}</code>
Direction: <b>{direction}</b>
Confidence Score: <code>{score}</code>

Reasons:
"""
        for reason in reasons:
            message += f"• {reason}\n"
            
        message += f"\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        return message 

    def format_prep_alert(self, symbol: str, direction: str, score: float, reasons: List[str]) -> str:
        emoji = "🟡"
        confidence = min(10, max(1, int(abs(score))))
        
        message = f"""
{emoji} <b>PREP TRADE: {symbol}</b>

Direction: <b>{direction}</b>
Confidence: {confidence}/10
Reason: {', '.join(reasons)}
"""
        return message

    def format_execute_alert(self, symbol: str, direction: str) -> str:
        emoji = "🟢"
        current_time = datetime.now().strftime("%H:%M:%S")
        
        message = f"""
{emoji} <b>EXECUTE NOW: {symbol}</b>

Action: <b>{direction}</b>
Time: {current_time}
Duration: 60 seconds
"""
        return message

    async def send_trade_alerts(self, symbol: str, direction: str, score: float, reasons: List[str]) -> None:
        if not self.is_configured():
            print("Telegram not configured")
            return

        prep_message = self.format_prep_alert(symbol, direction, score, reasons)
        if not self.send_message(prep_message):
            print(f"Failed to send PREP alert for {symbol}")
            return

        await asyncio.sleep(60)

        execute_message = self.format_execute_alert(symbol, direction)
        if not self.send_message(execute_message):
            print(f"Failed to send EXECUTE alert for {symbol}")
            return 