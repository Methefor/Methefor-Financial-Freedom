"""
MIDAS PRO v6.0 - Technical Analysis Module
RSI, MACD, Volume, Moving Averages ve daha fazlası
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import ta
import logging
from src.technical.patterns import PatternRecognizer

logger = logging.getLogger(__name__)


class TechnicalAnalyzer:
    """Teknik analiz göstergeleri hesaplama"""
    
    def __init__(self):
        self.pattern_recognizer = PatternRecognizer()
        """Initialize technical analyzer"""
        logger.info("[OK] Technical Analyzer başlatıldı")
    
    def get_stock_data(self, symbol: str, period: str = "1mo", interval: str = "1d") -> pd.DataFrame:
        """
        Hisse verilerini yfinance'dan çek
        
        Args:
            symbol: Hisse sembolü
            period: Veri periyodu (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, max)
            interval: Veri aralığı (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)
            
        Returns:
            DataFrame with OHLCV data
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"{symbol}: Veri bulunamadı")
                return pd.DataFrame()
            
            logger.info(f"[OK] {symbol}: {len(data)} bar veri çekildi")
            return data
            
        except Exception as e:
            logger.error(f"{symbol} veri hatası: {e}")
            return pd.DataFrame()
    
    def calculate_rsi(self, data: pd.DataFrame, period: int = 14) -> pd.Series:
        """
        RSI (Relative Strength Index) hesapla
        
        Args:
            data: Price data (Close column gerekli)
            period: RSI periyodu (default 14)
            
        Returns:
            RSI değerleri (0-100)
        """
        try:
            close = data['Close']
            
            # Fiyat değişimleri
            delta = close.diff()
            
            # Kazanç ve kayıplar
            gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
            
            # RS ve RSI
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"RSI hesaplama hatası: {e}")
            return pd.Series()
    
    def calculate_macd(self, data: pd.DataFrame, 
                       fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        MACD (Moving Average Convergence Divergence) hesapla
        
        Args:
            data: Price data
            fast: Hızlı EMA periyodu
            slow: Yavaş EMA periyodu
            signal: Signal line periyodu
            
        Returns:
            (macd_line, signal_line, histogram)
        """
        try:
            close = data['Close']
            
            # EMA hesaplamaları
            ema_fast = close.ewm(span=fast, adjust=False).mean()
            ema_slow = close.ewm(span=slow, adjust=False).mean()
            
            # MACD line
            macd_line = ema_fast - ema_slow
            
            # Signal line
            signal_line = macd_line.ewm(span=signal, adjust=False).mean()
            
            # Histogram
            histogram = macd_line - signal_line
            
            return macd_line, signal_line, histogram
            
        except Exception as e:
            logger.error(f"MACD hesaplama hatası: {e}")
            return pd.Series(), pd.Series(), pd.Series()
    
    def calculate_moving_averages(self, data: pd.DataFrame, 
                                   periods: List[int] = [20, 50, 200]) -> Dict[str, pd.Series]:
        """
        Moving averages (SMA) hesapla
        
        Args:
            data: Price data
            periods: MA periyotları
            
        Returns:
            Dictionary of MA values
        """
        try:
            close = data['Close']
            mas = {}
            
            for period in periods:
                mas[f'SMA_{period}'] = close.rolling(window=period).mean()
            
            return mas
            
        except Exception as e:
            logger.error(f"MA hesaplama hatası: {e}")
            return {}
    
    def calculate_volume_analysis(self, data: pd.DataFrame, period: int = 20) -> Dict:
        """
        Volume analizi yap
        
        Args:
            data: OHLCV data
            period: Average volume periyodu
            
        Returns:
            Volume metrics
        """
        try:
            volume = data['Volume']
            
            # Average volume
            avg_volume = volume.rolling(window=period).mean()
            
            # Son volume
            current_volume = volume.iloc[-1]
            avg_volume_current = avg_volume.iloc[-1]
            
            # Volume ratio
            volume_ratio = current_volume / avg_volume_current if avg_volume_current > 0 else 0
            
            # Volume trend (increasing/decreasing)
            volume_trend = volume.iloc[-5:].mean() / volume.iloc[-20:-5].mean() if len(volume) >= 20 else 1.0
            
            return {
                'current_volume': current_volume,
                'avg_volume': avg_volume_current,
                'volume_ratio': volume_ratio,
                'volume_trend': 'increasing' if volume_trend > 1.2 else 'decreasing' if volume_trend < 0.8 else 'stable',
                'volume_spike': volume_ratio > 1.5
            }
            
        except Exception as e:
            logger.error(f"Volume analizi hatası: {e}")
            return {}
    
    def calculate_bollinger_bands(self, data: pd.DataFrame, period: int = 20, std_dev: int = 2) -> Dict:
        """
        Bollinger Bands hesapla
        
        Args:
            data: Price data
            period: MA periyodu
            std_dev: Standart sapma çarpanı
            
        Returns:
            Upper, middle, lower bands
        """
        try:
            close = data['Close']
            
            # Middle band (SMA)
            middle_band = close.rolling(window=period).mean()
            
            # Standart sapma
            std = close.rolling(window=period).std()
            
            # Upper ve Lower bands
            upper_band = middle_band + (std * std_dev)
            lower_band = middle_band - (std * std_dev)
            
            # Son değerler
            current_price = close.iloc[-1]
            upper = upper_band.iloc[-1]
            middle = middle_band.iloc[-1]
            lower = lower_band.iloc[-1]
            
            # Bollinger band pozisyonu (0-100%)
            bb_position = ((current_price - lower) / (upper - lower) * 100) if upper != lower else 50
            
            return {
                'upper_band': upper,
                'middle_band': middle,
                'lower_band': lower,
                'current_price': current_price,
                'bb_position': bb_position,
                'oversold': bb_position < 20,
                'overbought': bb_position > 80
            }
            
        except Exception as e:
            logger.error(f"Bollinger Bands hatası: {e}")
            return {}
    
    def analyze_dataframe(self, symbol: str, data: pd.DataFrame) -> Dict:
        """
        Verilen DataFrame üzerinde teknik analiz yap (Backtest için uygun)
        """
        try:
            # RSI
            rsi = self.calculate_rsi(data)
            current_rsi = rsi.iloc[-1] if not rsi.empty else 50
            
            # MACD
            macd_line, signal_line, histogram = self.calculate_macd(data)
            current_macd = macd_line.iloc[-1] if not macd_line.empty else 0
            current_signal = signal_line.iloc[-1] if not signal_line.empty else 0
            current_histogram = histogram.iloc[-1] if not histogram.empty else 0
            
            # Moving Averages
            mas = self.calculate_moving_averages(data, periods=[20, 50, 200])
            current_price = data['Close'].iloc[-1]
            
            # MA crossovers
            ma_20 = mas['SMA_20'].iloc[-1] if 'SMA_20' in mas else current_price
            ma_50 = mas['SMA_50'].iloc[-1] if 'SMA_50' in mas else current_price
            ma_200 = mas['SMA_200'].iloc[-1] if 'SMA_200' in mas else current_price
            
            # Trend
            trend = 'bullish' if current_price > ma_50 > ma_200 else 'bearish' if current_price < ma_50 < ma_200 else 'neutral'
            
            # Volume
            volume_metrics = self.calculate_volume_analysis(data)
            
            # Bollinger Bands
            bb_metrics = self.calculate_bollinger_bands(data)
            
            # Price change
            price_change_1d = ((data['Close'].iloc[-1] / data['Close'].iloc[-2] - 1) * 100) if len(data) >= 2 else 0
            price_change_5d = ((data['Close'].iloc[-1] / data['Close'].iloc[-6] - 1) * 100) if len(data) >= 6 else 0
            
            # Technical signals
            signals = self._generate_technical_signals(
                current_rsi, current_macd, current_signal, current_histogram,
                trend, volume_metrics, bb_metrics
            )
            
            return {
                'symbol': symbol,
                'timestamp': data.index[-1].isoformat() if not data.empty else datetime.now().isoformat(),
                'price': {
                    'current': current_price,
                    'change_1d': price_change_1d,
                    'change_5d': price_change_5d
                },
                'rsi': {
                    'value': current_rsi,
                    'signal': 'oversold' if current_rsi < 30 else 'overbought' if current_rsi > 70 else 'neutral'
                },
                'macd': {
                    'macd_line': current_macd,
                    'signal_line': current_signal,
                    'histogram': current_histogram,
                    'signal': 'bullish' if current_histogram > 0 else 'bearish'
                },
                'moving_averages': {
                    'ma_20': ma_20,
                    'ma_50': ma_50,
                    'ma_200': ma_200,
                    'trend': trend
                },
                'volume': volume_metrics,
                'bollinger_bands': bb_metrics,
                'technical_signals': signals,
                'overall_score': signals['score'],
                'whale_alert': whale_alert, # Yeni eklenen alan
                'patterns': patterns # Placeholder for patterns, as it was in the original return
            }
            
        except Exception as e:
            logger.error(f"{symbol} analiz hatası: {e}")
            return {'error': str(e)}

    def analyze_symbol(self, symbol: str, period: str = "3mo") -> Dict:
        """
        Bir sembol için canlı teknik analiz yap
        """
        logger.info(f"[TECH] {symbol} teknik analiz başlatılıyor...")
        
        # 1. Veri Çekme
        try:
            # yfinance bazen sembol bulunsa bile 'no data' hatası verebiliyor
            # veya internal index error fırlatabiliyor.
            ticker = yf.Ticker(symbol)
            
            # Geçmiş verisi (1 yıl)
            hist = ticker.history(period="1y")
            
            if hist.empty:
                logger.warning(f"No historical data for {symbol}")
                return {'error': 'No data'}
            
        except Exception as e:
            logger.warning(f"yfinance error for {symbol}: {str(e)}")
            return {'error': f'Data fetch error: {str(e)}'}
            
        # 2. Analiz et
        return self.analyze_dataframe(symbol, hist)
    
    def _generate_technical_signals(self, rsi: float, macd: float, signal: float, 
                                      histogram: float, trend: str, volume: Dict, bb: Dict) -> Dict:
        """
        Teknik göstergelere göre AL/SAT sinyali üret
        
        Returns:
            Signal with score (0-100)
        """
        score = 50  # Başlangıç nötr
        signals = []
        
        # RSI sinyalleri
        if rsi < 30:
            score += 15
            signals.append("RSI oversold (bullish)")
        elif rsi > 70:
            score -= 15
            signals.append("RSI overbought (bearish)")
        
        # MACD sinyalleri
        if histogram > 0:
            score += 10
            signals.append("MACD bullish")
        else:
            score -= 10
            signals.append("MACD bearish")
        
        # Trend
        if trend == 'bullish':
            score += 15
            signals.append("Uptrend")
        elif trend == 'bearish':
            score -= 15
            signals.append("Downtrend")
        
        # Volume
        if volume.get('volume_spike', False):
            score += 10
            signals.append("Volume spike")
        
        # Bollinger Bands
        if bb.get('oversold', False):
            score += 10
            signals.append("BB oversold")
        elif bb.get('overbought', False):
            score -= 10
            signals.append("BB overbought")
        
        # Normalize score (0-100)
        score = max(0, min(100, score))
        
        # Signal decision
        if score >= 70:
            decision = 'STRONG BUY'
        elif score >= 60:
            decision = 'BUY'
        elif score >= 40:
            decision = 'HOLD'
        elif score >= 30:
            decision = 'SELL'
        else:
            decision = 'STRONG SELL'
        
        return {
            'decision': decision,
            'score': score,
            'signals': signals
        }


def main():
    """Test fonksiyonu"""
    print("=== MIDAS PRO v6.0 - Technical Analysis Test ===\n")
    
    analyzer = TechnicalAnalyzer()
    
    # Test sembolleri
    symbols = ['AAPL', 'TSLA', 'BTC-USD']
    
    for symbol in symbols:
        print(f"\n{'='*60}")
        print(f"[TECH] {symbol} TEKNİK ANALİZ")
        print(f"{'='*60}\n")
        
        analysis = analyzer.analyze_symbol(symbol)
        
        if 'error' in analysis:
            print(f"[X] Hata: {analysis['error']}")
            continue
        
        # Sonuçları göster
        print(f"[PRICE] Fiyat: ${analysis['price']['current']:.2f}")
        print(f"   1 Gün: {analysis['price']['change_1d']:+.2f}%")
        print(f"   5 Gün: {analysis['price']['change_5d']:+.2f}%")
        
        print(f"\n[BUY] RSI: {analysis['rsi']['value']:.1f} ({analysis['rsi']['signal']})")
        print(f"[TECH] MACD: {analysis['macd']['signal']}")
        print(f"[SELL] Trend: {analysis['moving_averages']['trend'].upper()}")
        print(f"📦 Volume: {analysis['volume']['volume_trend']}")
        
        signals = analysis['technical_signals']
        decision_emoji = {'STRONG BUY': '[STRONG-BUY]', 'BUY': '[BUY]', 'HOLD': '[HOLD]', 
                          'SELL': '[SELL]', 'STRONG SELL': '[STRONG-SELL]'}
        
        print(f"\n{decision_emoji.get(signals['decision'], '•')} SİNYAL: {signals['decision']}")
        print(f"   Skor: {signals['score']}/100")
        print(f"   Göstergeler:")
        for sig in signals['signals']:
            print(f"      • {sig}")
    
    print(f"\n{'='*60}")
    print("[OK] Teknik analiz test tamamlandı!")


if __name__ == "__main__":
    main()
