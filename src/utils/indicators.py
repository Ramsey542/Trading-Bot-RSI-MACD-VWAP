import numpy as np
from typing import List, Dict, Union, Optional, Tuple
import sys
from pathlib import Path

root_dir = str(Path(__file__).resolve().parent.parent.parent)
if root_dir not in sys.path:
    sys.path.append(root_dir)

from src.models.candle import Candle
from config.config import Config

class TechnicalIndicators:
    @staticmethod
    def calculate_rsi(candles: List[Candle], period: int = Config.RSI_PERIOD) -> float:
        """
    Calculates the Relative Strength Index (RSI) using Wilder's formula:
    1. Calculate price changes and split into gains/losses
    2. Calculate average gain/loss over initial period
    3. Use smoothed moving average for subsequent periods: 
       avg = (prev_avg * (period-1) + current) / period
    4. RSI = 100 - (100 / (1 + RS)) where RS = avg_gain / avg_loss
        """    
        closes = [candle.close for candle in candles]
        deltas = np.diff(closes)
        
        gain = np.where(deltas > 0, deltas, 0)
        loss = np.where(deltas < 0, -deltas, 0)
        
        avg_gain = np.mean(gain[:period])
        avg_loss = np.mean(loss[:period])
        
        for i in range(period, len(gain)):
            avg_gain = (avg_gain * (period - 1) + gain[i]) / period
            avg_loss = (avg_loss * (period - 1) + loss[i]) / period
        
        if avg_loss == 0:
            return 100
        
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def get_macd_trend(candles: List[Candle]) -> str:
        macd_data = TechnicalIndicators.calculate_macd(candles)
        macd_line = macd_data["macd_line"]
        signal_line = macd_data["signal_line"]
        return "bullish" if macd_line[-1] > signal_line[-1] else "bearish"

    @staticmethod
    def calculate_macd(candles: List[Candle]) -> Dict[str, Union[bool, np.ndarray]]:
        closes = np.array([candle.close for candle in candles])
        
        ema12 = np.zeros_like(closes)
        ema26 = np.zeros_like(closes)
        
        multiplier12 = 2 / (Config.MACD_FAST + 1)
        ema12[0] = closes[0]
        for i in range(1, len(closes)):
            ema12[i] = (closes[i] - ema12[i-1]) * multiplier12 + ema12[i-1]
        
        multiplier26 = 2 / (Config.MACD_SLOW + 1)
        ema26[0] = closes[0]
        for i in range(1, len(closes)):
            ema26[i] = (closes[i] - ema26[i-1]) * multiplier26 + ema26[i-1]
        
        macd_line = ema12 - ema26
        
        signal_line = np.zeros_like(macd_line)
        multiplier9 = 2 / (Config.MACD_SIGNAL + 1)
        signal_line[0] = macd_line[0]
        for i in range(1, len(macd_line)):
            signal_line[i] = (macd_line[i] - signal_line[i-1]) * multiplier9 + signal_line[i-1]
        
        current_cross = macd_line[-1] > signal_line[-1]
        prev_cross = macd_line[-2] > signal_line[-2]
        
        return {
            "MACD_cross": current_cross != prev_cross,
            "macd_line": macd_line,
            "signal_line": signal_line
        }

    @staticmethod
    def calculate_vwap(candles: List[Candle]) -> Dict[str, str]:
        """
        Calculates Volume Weighted Average Price (VWAP):
        1. For each candle: typical_price = (high + low + close) / 3
        2. Multiply typical price by volume for each candle
        3. Sum all price-volume products and divide by total volume
        4. Compare current price to VWAP to determine trend
        """
        cumulative_pv = 0
        cumulative_volume = 0
        
        for candle in candles:
            typical_price = (candle.high + candle.low + candle.close) / 3
            cumulative_pv += typical_price * candle.volume
            cumulative_volume += candle.volume
        
        vwap = cumulative_pv / cumulative_volume if cumulative_volume > 0 else 0
        current_price = candles[-1].close
        
        return {"VWAP_trend": "above" if current_price > vwap else "below"}

    @staticmethod
    def calculate_bollinger_bands(
        candles: List[Candle], 
        period: int = Config.BOLLINGER_PERIOD, 
        std_dev: float = Config.BOLLINGER_STD
    ) -> Dict[str, Union[str, Dict]]:
        """
        Calculates Bollinger Bands using price and standard deviation:
        1. Middle Band = 20-period Simple Moving Average (SMA)
        2. Upper Band = Middle Band + (2 * Standard Deviation)
        3. Lower Band = Middle Band - (2 * Standard Deviation)
        4. Returns band values and whether price touches upper/lower bands
        """

        closes = np.array([candle.close for candle in candles])
        
        middle_band = np.mean(closes[-period:])
        std = np.std(closes[-period:])
        
        upper_band = middle_band + (std_dev * std)
        lower_band = middle_band - (std_dev * std)
        
        current_price = closes[-1]
        
        bands = {
            "upper": upper_band,
            "middle": middle_band,
            "lower": lower_band
        }
        
        if current_price >= upper_band:
            touch = "upper"
        elif current_price <= lower_band:
            touch = "lower"
        else:
            touch = "none"
            
        return {"bollinger_touch": touch, "bands": bands}

    @staticmethod
    def is_volume_spike(candles: List[Candle], lookback: int = 10, threshold: float = 1.5) -> bool:
        if len(candles) < lookback + 1:
            return False
        volumes = [candle.volume for candle in candles[-lookback-1:-1]]
        avg_volume = sum(volumes) / len(volumes)
        return candles[-1].volume > threshold * avg_volume

    @staticmethod
    def is_bollinger_squeeze(bands: Dict[str, float], threshold: float = 0.05) -> bool:
        return (bands["upper"] - bands["lower"]) / bands["middle"] < threshold

    @staticmethod
    def is_vwap_aligned(price: float, vwap: float, threshold: float = 0.01) -> bool:
        return abs(price - vwap) / vwap < threshold

    @staticmethod
    def detect_trend_structure(candles: List[Candle]) -> str:
        if len(candles) < 4:
            return "neutral"
        highs = [candle.high for candle in candles[-4:]]
        lows = [candle.low for candle in candles[-4:]]
        return "uptrend" if highs[-1] > highs[-2] and lows[-1] > lows[-2] else "downtrend"

    @staticmethod
    def is_strong_candle(candle: Candle) -> bool:
        body = abs(candle.close - candle.open)
        wick_total = candle.high - candle.low
        return body / wick_total > 0.6 if wick_total > 0 else False

    @staticmethod
    def analyze_volume_spike(
        candles: List[Candle], 
        lookback: int = Config.VOLUME_LOOKBACK, 
        threshold: float = Config.VOLUME_THRESHOLD
    ) -> Dict[str, bool]:
        """
        Detects significant volume increases:
        1. Calculate average volume over lookback period (default 20 candles)
        2. Compare current volume to average volume
        3. Signal volume spike if current volume > threshold * average volume
        """

        volumes = [candle.volume for candle in candles]
        avg_volume = np.mean(volumes[-lookback:-1]) 
        current_volume = volumes[-1]
        
        return {"volume_spike": current_volume > (avg_volume * threshold)}

    @staticmethod
    def analyze_price_action(candles: List[Candle], bollinger: Optional[Dict] = None) -> Dict[str, str]:
        """
        Analyze candlestick patterns and price momentum using last 5 candles on 1-5 minute timeframe.
        
        BULLISH if:
        - 3 or more candles are green (close > open), OR
        - Bullish engulfing (last candle engulfs previous), OR
        - Price bounces off lower Bollinger Band
        
        BEARISH if:
        - 3 or more candles are red (close < open), OR
        - Bearish engulfing pattern, OR
        - Rejection from upper Bollinger Band
        
        Returns "neutral" if none apply
        """
        green_count = 0
        red_count = 0
        
        last_candles = candles[-5:]
        for candle in last_candles:
            if candle.close > candle.open:
                green_count += 1
            elif candle.close < candle.open:
                red_count += 1
        
        if green_count >= 3:
            return {"price_action": "bullish", "reason": "3+ green candles"}
            
        if len(candles) >= 2:
            current = candles[-1]
            previous = candles[-2]
            if (current.close > current.open and  
                current.open < previous.close and  
                current.close > previous.open and  
                current.open < previous.close and  
                current.close > previous.open):    
                return {"price_action": "bullish", "reason": "bullish engulfing"}
                
        if bollinger and bollinger.get("bands"):
            current_price = candles[-1].close
            previous_price = candles[-2].close
            lower_band = bollinger["bands"]["lower"]
            if (previous_price <= lower_band and 
                current_price > lower_band):
                return {"price_action": "bullish", "reason": "Bollinger bounce"}
        
        if red_count >= 3:
            return {"price_action": "bearish", "reason": "3+ red candles"}
            
        if len(candles) >= 2:
            current = candles[-1]
            previous = candles[-2]
            if (current.close < current.open and  
                current.open > previous.close and 
                current.close < previous.open and  
                current.open > previous.close and 
                current.close < previous.open):    
                return {"price_action": "bearish", "reason": "bearish engulfing"}
                
        if bollinger and bollinger.get("bands"):
            current_price = candles[-1].close
            previous_price = candles[-2].close
            upper_band = bollinger["bands"]["upper"]
            if (previous_price >= upper_band and 
                current_price < upper_band):
                return {"price_action": "bearish", "reason": "Bollinger rejection"}
        
        return {"price_action": "neutral", "reason": "no clear pattern"}

    @classmethod
    def calculate_all_indicators(cls, candles: List[Candle]) -> Tuple[float, List[str], Dict]:
        if not candles:
            return 0, ["No data available"], {}
            
        indicators = {}
        score = 0
        reasons = []
        indicator_values = {}

        rsi_value = cls.calculate_rsi(candles)
        indicators["RSI"] = rsi_value
        indicator_values["RSI"] = round(rsi_value, 2)

        macd_data = cls.calculate_macd(candles)
        macd_trend = cls.get_macd_trend(candles)
        indicators["MACD_cross"] = macd_data["MACD_cross"]
        indicators["MACD_trend"] = macd_trend
        indicator_values["MACD"] = round(macd_data["macd_line"][-1], 2)

        bollinger = cls.calculate_bollinger_bands(candles)
        current_price = candles[-1].close
        middle_band = bollinger["bands"]["middle"]
        indicators.update(bollinger)
        
        bb_value = ((current_price - middle_band) / middle_band) * 100
        indicator_values["BB"] = round(bb_value, 2)

        vwap_data = cls.calculate_vwap(candles)
        indicators.update(vwap_data)
        
        is_squeeze = cls.is_bollinger_squeeze(bollinger["bands"])
        indicators["bollinger_squeeze"] = is_squeeze
        
        is_spike = cls.is_volume_spike(candles)
        indicators["volume_spike_new"] = is_spike
        
        trend_structure = cls.detect_trend_structure(candles)
        indicators["trend_structure"] = trend_structure
        
        is_strong = cls.is_strong_candle(candles[-1])
        indicators["strong_candle"] = is_strong

        if indicators["RSI"] < 30:
            score += 2
            reasons.append("RSI oversold")
        elif indicators["RSI"] > 70:
            score -= 2
            reasons.append("RSI overbought")

        if indicators["MACD_cross"]:
            if macd_trend == "bullish":
                score += 3
                reasons.append("MACD bull cross")
            else:
                score -= 3
                reasons.append("MACD bear cross")

        if indicators["VWAP_trend"] == "above":
            score += 2
            reasons.append("VWAP uptrend")
        elif indicators["VWAP_trend"] == "below":
            score -= 2
            reasons.append("VWAP downtrend")

        if indicators["bollinger_touch"] == "lower":
            score += 1
            reasons.append("BB bounce")
        elif indicators["bollinger_touch"] == "upper":
            score -= 1
            reasons.append("BB reject")

        if indicators["bollinger_squeeze"]:
            score += 1
            reasons.append("BB squeeze")

        if indicators["volume_spike_new"]:
            if trend_structure == "uptrend":
                score += 2
                reasons.append("VOL spike up")
            elif trend_structure == "downtrend":
                score -= 2
                reasons.append("VOL spike down")

        if indicators["trend_structure"] == "uptrend":
            score += 2
            reasons.append("HH/HL")
        elif indicators["trend_structure"] == "downtrend":
            score -= 2
            reasons.append("LL/LH")

        if indicators["strong_candle"]:
            if trend_structure == "uptrend":
                score += 1
                reasons.append("Strong bull")
            elif trend_structure == "downtrend":
                score -= 1
                reasons.append("Strong bear")

        return score, reasons, indicator_values 