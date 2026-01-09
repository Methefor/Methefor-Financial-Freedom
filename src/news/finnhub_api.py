"""
MIDAS PRO v6.0 - Finnhub News API Integration
Real-time market news ve company news
"""

import requests
import aiohttp
import asyncio
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class FinnhubNewsAPI:
    """Finnhub API ile gerçek zamanlı haber toplama"""
    
    def __init__(self, api_key: str = None, config_path: str = "config/api_keys.json"):
        """
        Args:
            api_key: Finnhub API key
            config_path: API keys config dosyası
        """
        if api_key:
            self.api_key = api_key
        else:
            # Config'den oku
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    self.api_key = config.get('finnhub', {}).get('api_key', '')
            except Exception as e:
                logger.error(f"API key yüklenemedi: {e}")
                self.api_key = ''
        
        self.base_url = "https://finnhub.io/api/v1"
        self.session = requests.Session()
        
        if not self.api_key or self.api_key == "YOUR_FINNHUB_API_KEY_HERE":
            logger.warning("⚠️ Finnhub API key ayarlanmamış!")
            logger.info("📝 API key almak için: https://finnhub.io/register")
        else:
            logger.info("[OK] Finnhub API başlatıldı")

    async def _fetch_async(self, session, url, params):
        """Async HTTP request helper"""
        try:
            async with session.get(url, params=params, timeout=10) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            logger.error(f"Async request error ({url}): {e}")
            return None

    async def get_market_news_async(self, session: aiohttp.ClientSession, category: str = "general") -> List[Dict]:
        """
        Asenkron genel piyasa haberlerini getir
        """
        if not self.api_key or self.api_key == "YOUR_FINNHUB_API_KEY_HERE":
            return self._get_mock_news()
        
        url = f"{self.base_url}/news"
        params = {
            'category': category,
            'token': self.api_key
        }
        
        data = await self._fetch_async(session, url, params)
        if not data:
            return []
            
        formatted_news = []
        for item in data:
            formatted_news.append({
                'source': item.get('source', 'Finnhub'),
                'title': item.get('headline', ''),
                'summary': item.get('summary', ''),
                'link': item.get('url', ''),
                'published': datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                'category': item.get('category', category),
                'related_symbols': item.get('related', '').split(',') if item.get('related') else [],
                'timestamp': datetime.now().isoformat()
            })
        return formatted_news

    async def get_company_news_async(self, session: aiohttp.ClientSession, symbol: str, days_back: int = 7) -> List[Dict]:
        """
        Asenkron şirket haberlerini getir
        """
        if not self.api_key:
            return []
        
        to_date = datetime.now()
        from_date = to_date - timedelta(days=days_back)
        
        url = f"{self.base_url}/company-news"
        params = {
            'symbol': symbol.upper(),
            'from': from_date.strftime('%Y-%m-%d'),
            'to': to_date.strftime('%Y-%m-%d'),
            'token': self.api_key
        }
        
        data = await self._fetch_async(session, url, params)
        if not data:
            return []
            
        formatted_news = []
        for item in data:
            formatted_news.append({
                'source': item.get('source', 'Finnhub'),
                'title': item.get('headline', ''),
                'summary': item.get('summary', ''),
                'link': item.get('url', ''),
                'published': datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                'category': 'company',
                'matched_symbol': symbol.upper(),
                'timestamp': datetime.now().isoformat()
            })
        return formatted_news
    
    async def get_watchlist_news_async(self, symbols: List[str], days_back: int = 3) -> List[Dict]:
        """
        Tüm watchlist için parallel haber çekme
        """
        async with aiohttp.ClientSession() as session:
            tasks = [self.get_company_news_async(session, symbol, days_back) for symbol in symbols]
            results = await asyncio.gather(*tasks)
            
            all_news = []
            for news_list in results:
                all_news.extend(news_list)
            
            # Sort by date
            all_news.sort(key=lambda x: x['published'], reverse=True)
            return all_news

    # ... (Keep existing sync methods for compatibility if needed, or we can rely on async from now on)
    
    def get_market_news(self, category: str = "general", min_id: int = 0) -> List[Dict]:
        """
        Genel piyasa haberlerini getir
        
        Args:
            category: general, forex, crypto, merger
            min_id: Minimum news ID (pagination için)
            
        Returns:
            Haber listesi
        """
        if not self.api_key or self.api_key == "YOUR_FINNHUB_API_KEY_HERE":
            logger.warning("API key bulunamadı, örnek veri döndürülüyor")
            return self._get_mock_news()
        
        try:
            url = f"{self.base_url}/news"
            params = {
                'category': category,
                'token': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            news_items = response.json()
            
            # Format'a çevir
            formatted_news = []
            for item in news_items:
                formatted_news.append({
                    'id': item.get('id', 0),
                    'source': item.get('source', 'Finnhub'),
                    'title': item.get('headline', ''),
                    'summary': item.get('summary', ''),
                    'link': item.get('url', ''),
                    'published': datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                    'category': item.get('category', category),
                    'image': item.get('image', ''),
                    'related_symbols': item.get('related', '').split(',') if item.get('related') else [],
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"[OK] Finnhub: {len(formatted_news)} piyasa haberi toplandı")
            return formatted_news
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Finnhub API hatası: {e}")
            return []
        except Exception as e:
            logger.error(f"Beklenmeyen hata: {e}")
            return []
    
    def get_company_news(self, symbol: str, days_back: int = 7) -> List[Dict]:
        """
        Belirli bir şirketin haberlerini getir
        
        Args:
            symbol: Hisse sembolü (örn: AAPL, TSLA)
            days_back: Kaç gün geriye bakılacak
            
        Returns:
            Şirkete özel haberler
        """
        if not self.api_key or self.api_key == "YOUR_FINNHUB_API_KEY_HERE":
            return []
        
        try:
            # Tarih aralığı
            to_date = datetime.now()
            from_date = to_date - timedelta(days=days_back)
            
            url = f"{self.base_url}/company-news"
            params = {
                'symbol': symbol.upper(),
                'from': from_date.strftime('%Y-%m-%d'),
                'to': to_date.strftime('%Y-%m-%d'),
                'token': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            news_items = response.json()
            
            # Format'a çevir
            formatted_news = []
            for item in news_items:
                formatted_news.append({
                    'id': item.get('id', 0),
                    'source': item.get('source', 'Finnhub'),
                    'title': item.get('headline', ''),
                    'summary': item.get('summary', ''),
                    'link': item.get('url', ''),
                    'published': datetime.fromtimestamp(item.get('datetime', 0)).isoformat(),
                    'category': item.get('category', 'company'),
                    'image': item.get('image', ''),
                    'matched_symbol': symbol.upper(),
                    'timestamp': datetime.now().isoformat()
                })
            
            logger.info(f"[OK] {symbol}: {len(formatted_news)} şirket haberi toplandı")
            return formatted_news
            
        except Exception as e:
            logger.error(f"{symbol} haber hatası: {e}")
            return []
    
    def get_crypto_news(self) -> List[Dict]:
        """Kripto para haberlerini getir"""
        return self.get_market_news(category='crypto')
    
    def get_forex_news(self) -> List[Dict]:
        """Forex haberlerini getir"""
        return self.get_market_news(category='forex')
    
    def get_watchlist_news(self, symbols: List[str], days_back: int = 3) -> List[Dict]:
        """
        Watchlist'teki tüm semboller için haber topla
        
        Args:
            symbols: Sembol listesi
            days_back: Kaç gün geriye bakılacak
            
        Returns:
            Tüm haberleri birleştirilmiş liste
        """
        all_news = []
        
        for symbol in symbols:
            news = self.get_company_news(symbol, days_back)
            all_news.extend(news)
            time.sleep(0.5)  # Rate limiting
        
        # Tarih'e göre sırala (en yeni önce)
        all_news.sort(key=lambda x: x['published'], reverse=True)
        
        logger.info(f"[OK] Watchlist: {len(all_news)} toplam haber")
        return all_news
    
    def _get_mock_news(self) -> List[Dict]:
        """API key yoksa mock data döndür"""
        logger.info("[NEWS] Mock news data döndürülüyor (API key yok)")
        
        mock_news = [
            {
                'id': 1,
                'source': 'Finnhub (Mock)',
                'title': 'Market opens higher on positive economic data',
                'summary': 'Stock markets rallied today as investors digested strong employment numbers',
                'link': 'https://example.com/news1',
                'published': datetime.now().isoformat(),
                'category': 'general',
                'image': '',
                'related_symbols': ['SPY', 'QQQ'],
                'timestamp': datetime.now().isoformat()
            }
        ]
        
        return mock_news
    
    def get_quote(self, symbol: str) -> Dict:
        """
        Hisse fiyat bilgisi getir
        
        Args:
            symbol: Hisse sembolü
            
        Returns:
            Fiyat bilgisi
        """
        if not self.api_key or self.api_key == "YOUR_FINNHUB_API_KEY_HERE":
            return {}
        
        try:
            url = f"{self.base_url}/quote"
            params = {
                'symbol': symbol.upper(),
                'token': self.api_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            
            return {
                'symbol': symbol.upper(),
                'current_price': data.get('c', 0),
                'change': data.get('d', 0),
                'percent_change': data.get('dp', 0),
                'high': data.get('h', 0),
                'low': data.get('l', 0),
                'open': data.get('o', 0),
                'previous_close': data.get('pc', 0),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"{symbol} quote hatası: {e}")
            return {}


def main():
    """Test fonksiyonu"""
    print("=== MIDAS PRO v6.0 - Finnhub News API Test ===\n")
    
    # API'yi başlat
    api = FinnhubNewsAPI()
    
    # Async testi
    print("\n[ASYNC] Async haber toplama testi...")
    async def run_async_test():
        async with aiohttp.ClientSession() as session:
            news = await api.get_market_news_async(session)
            print(f"Async Market News: {len(news)} items")
            
            company_news = await api.get_company_news_async(session, 'AAPL')
            print(f"Async AAPL News: {len(company_news)} items")
    
    asyncio.run(run_async_test())

    # 1. Genel piyasa haberleri
    print("[NEWS] Genel Piyasa Haberleri:\n")
    market_news = api.get_market_news(category='general')
    
    for i, news in enumerate(market_news[:5], 1):
        print(f"{i}. [{news['source']}] {news['title']}")
        print(f"   Link: {news['link']}")
        print()
    
    # 2. Kripto haberleri
    print("\n[CRYPTO] Kripto Haberleri:\n")
    crypto_news = api.get_crypto_news()
    
    for i, news in enumerate(crypto_news[:3], 1):
        print(f"{i}. {news['title']}")
        print()
    
    # 3. Belirli bir şirket
    print("\n🎯 AAPL Şirket Haberleri:\n")
    aapl_news = api.get_company_news('AAPL', days_back=3)
    
    for i, news in enumerate(aapl_news[:3], 1):
        print(f"{i}. {news['title']}")
        print()
    
    print(f"\n[OK] Test tamamlandı!")


if __name__ == "__main__":
    main()
