"""
METHEFOR FİNANSAL ÖZGÜRLÜK - Discovery Engine
Yeni fırsatları otomatik keşfeder
"""

import yfinance as yf
import requests
from datetime import datetime, timedelta
import logging
from typing import List, Dict
import time

logger = logging.getLogger(__name__)


class DiscoveryEngine:
    """Yeni trading fırsatlarını otomatik keşfeden sistem"""
    
    def __init__(self, config: dict = None):
        self.config = config or {}
        self.discovered_symbols = []
        
    def get_yahoo_trending(self) -> List[str]:
        """Yahoo Finance trending sembolleri al"""
        try:
            logger.info("[DISCOVERY] Yahoo Finance trending sembolleri alınıyor...")
            
            # Yahoo Finance trending tickers API
            url = "https://query1.finance.yahoo.com/v1/finance/trending/US"
            headers = {'User-Agent': 'Mozilla/5.0'}
            
            response = requests.get(url, headers=headers, timeout=10)
            data = response.json()
            
            symbols = []
            if 'finance' in data and 'result' in data['finance']:
                for item in data['finance']['result'][0].get('quotes', []):
                    symbol = item.get('symbol')
                    if symbol:
                        symbols.append(symbol)
            
            logger.info(f"[OK] {len(symbols)} trending sembol bulundu")
            return symbols[:10]
            
        except Exception as e:
            logger.error(f"[ERROR] Yahoo trending hatası: {e}")
            return []
    
    def get_top_gainers(self, limit: int = 10) -> List[Dict]:
        """En çok yükselen hisseleri bul"""
        try:
            logger.info("[DISCOVERY] Top gainers aranıyor...")
            
            # Finviz screener alternatifi - yfinance ile major indices
            major_symbols = [
                'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'NVDA', 'META', 'TSLA', 
                'AMD', 'PLTR', 'HOOD', 'MSTR', 'COIN', 'RIOT', 'MARA',
                'SQ', 'PYPL', 'SOFI', 'UPST', 'AFRM', 'SHOP'
            ]
            
            gainers = []
            for symbol in major_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='1d')
                    
                    if len(hist) > 0:
                        change_pct = ((hist['Close'].iloc[-1] - hist['Open'].iloc[0]) / 
                                     hist['Open'].iloc[0] * 100)
                        volume = hist['Volume'].iloc[-1]
                        
                        if change_pct > 5.0:  # 5%+ artış
                            gainers.append({
                                'symbol': symbol,
                                'change_pct': change_pct,
                                'volume': volume,
                                'price': hist['Close'].iloc[-1]
                            })
                    
                    time.sleep(0.2)
                    
                except Exception as e:
                    continue
            
            gainers.sort(key=lambda x: x['change_pct'], reverse=True)
            logger.info(f"[OK] {len(gainers)} gainer bulundu")
            return gainers[:limit]
            
        except Exception as e:
            logger.error(f"[ERROR] Top gainers hatası: {e}")
            return []
    
    def get_high_volume_stocks(self, limit: int = 10) -> List[Dict]:
        """Yüksek hacimli hisseleri bul"""
        try:
            logger.info("[DISCOVERY] Yüksek hacimli hisseler aranıyor...")
            
            major_symbols = [
                'SPY', 'QQQ', 'NVDA', 'TSLA', 'AAPL', 'AMD', 'PLTR',
                'MSTR', 'COIN', 'HOOD', 'SOFI', 'F', 'BAC', 'T',
                'INTC', 'SNAP', 'PINS', 'UBER', 'LYFT', 'DKNG'
            ]
            
            high_volume = []
            for symbol in major_symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period='5d')
                    
                    if len(hist) >= 5:
                        avg_volume = hist['Volume'][:-1].mean()
                        current_volume = hist['Volume'].iloc[-1]
                        volume_ratio = current_volume / avg_volume if avg_volume > 0 else 0
                        
                        if volume_ratio > 2.0:  # 2x normal hacim
                            high_volume.append({
                                'symbol': symbol,
                                'volume_ratio': volume_ratio,
                                'current_volume': current_volume,
                                'avg_volume': avg_volume
                            })
                    
                    time.sleep(0.2)
                    
                except Exception as e:
                    continue
            
            high_volume.sort(key=lambda x: x['volume_ratio'], reverse=True)
            logger.info(f"[OK] {len(high_volume)} yüksek hacimli hisse bulundu")
            return high_volume[:limit]
            
        except Exception as e:
            logger.error(f"[ERROR] High volume hatası: {e}")
            return []
    
    def discover_opportunities(self) -> List[str]:
        """Tüm keşif yöntemlerini kullan ve yeni fırsatları bul"""
        logger.info("\n" + "="*70)
        logger.info("[DISCOVERY] YENİ FIRSATLAR KEŞFEDİLİYOR")
        logger.info("="*70)
        
        all_discoveries = set()
        
        # 1. Trending symbols
        trending = self.get_yahoo_trending()
        all_discoveries.update(trending)
        
        # 2. Top gainers
        gainers = self.get_top_gainers(limit=10)
        all_discoveries.update([g['symbol'] for g in gainers])
        
        # 3. High volume
        high_vol = self.get_high_volume_stocks(limit=10)
        all_discoveries.update([h['symbol'] for h in high_vol])
        
        # Mevcut watchlist'le karşılaştır
        discovered = list(all_discoveries)
        
        logger.info(f"\n[OK] Toplam {len(discovered)} yeni sembol keşfedildi:")
        for symbol in discovered[:10]:
            logger.info(f"   - {symbol}")
        
        self.discovered_symbols = discovered
        return discovered
    
    def filter_discoveries(self, symbols: List[str], 
                          min_volume: int = 1000000,
                          min_price: float = 5.0,
                          max_price: float = 1000.0) -> List[str]:
        """Keşfedilen sembolleri filtrele"""
        logger.info("\n[FILTER] Keşifler filtreleniyor...")
        
        filtered = []
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='1d')
                
                if len(hist) > 0:
                    price = hist['Close'].iloc[-1]
                    volume = hist['Volume'].iloc[-1]
                    
                    if (volume >= min_volume and 
                        min_price <= price <= max_price):
                        filtered.append(symbol)
                        logger.info(f"[OK] {symbol}: ${price:.2f}, Vol: {volume:,.0f}")
                
                time.sleep(0.2)
                
            except Exception as e:
                continue
        
        logger.info(f"\n[OK] {len(filtered)}/{len(symbols)} sembol filtrelendi")
        return filtered


def main():
    """Test discovery engine"""
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    engine = DiscoveryEngine()
    
    # Keşif yap
    discoveries = engine.discover_opportunities()
    
    # Filtrele
    filtered = engine.filter_discoveries(
        discoveries,
        min_volume=1000000,
        min_price=5.0,
        max_price=500.0
    )
    
    print("\n" + "="*70)
    print("FİNAL KEŞİFLER:")
    print("="*70)
    for i, symbol in enumerate(filtered[:20], 1):
        print(f"{i}. {symbol}")


if __name__ == "__main__":
    main()
