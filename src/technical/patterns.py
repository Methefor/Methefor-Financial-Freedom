import pandas as pd
import numpy as np

class PatternRecognizer:
    def __init__(self):
        pass

    def check_patterns(self, df: pd.DataFrame) -> dict:
        """
        DataFrame üzerinde mum formasyonlarını tarar.
        Son mum için sonuç döner.
        """
        if df is None or len(df) < 5:
            return {}
        
        # Son iki mum
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        patterns = {
            'doji': self.is_doji(curr),
            'hammer': self.is_hammer(curr),
            'engulfing_bullish': self.is_bullish_engulfing(curr, prev),
            'engulfing_bearish': self.is_bearish_engulfing(curr, prev)
        }
        
        # Sadece bulunanları filtrele
        found_patterns = [k for k, v in patterns.items() if v]
        
        return {
            'found': len(found_patterns) > 0,
            'patterns': found_patterns,
            'description': ", ".join([p.replace('_', ' ').title() for p in found_patterns])
        }

    def is_doji(self, candle):
        """Doji: Açılış ve Kapanış çok yakın"""
        body = abs(candle['Close'] - candle['Open'])
        range_len = candle['High'] - candle['Low']
        return body <= range_len * 0.1

    def is_hammer(self, candle):
        """Hammer: Küçük gövde, uzun alt fitil"""
        body = abs(candle['Close'] - candle['Open'])
        lower_shadow = min(candle['Close'], candle['Open']) - candle['Low']
        upper_shadow = candle['High'] - max(candle['Close'], candle['Open'])
        
        return lower_shadow >= body * 2 and upper_shadow <= body * 0.5

    def is_bullish_engulfing(self, curr, prev):
        """Yutan Boğa: Önceki kırmızı, şimdiki yeşil ve kapsıyor"""
        prev_red = prev['Close'] < prev['Open']
        curr_green = curr['Close'] > curr['Open']
        
        engulfing = (curr['Open'] <= prev['Close']) and (curr['Close'] >= prev['Open'])
        
        return prev_red and curr_green and engulfing

    def is_bearish_engulfing(self, curr, prev):
        """Yutan Ayı: Önceki yeşil, şimdiki kırmızı ve kapsıyor"""
        prev_green = prev['Close'] > prev['Open']
        curr_red = curr['Close'] < curr['Open']
        
        engulfing = (curr['Open'] >= prev['Close']) and (curr['Close'] <= prev['Open'])
        
        return prev_green and curr_red and engulfing
