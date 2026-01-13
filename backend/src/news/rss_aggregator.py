"""
MIDAS PRO v5.0 - RSS News Aggregator
Çoklu kaynaklardan haber toplama ve filtreleme
"""

import feedparser
import json
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from pathlib import Path

# Logging ayarları
import os
log_dir = 'logs'
os.makedirs(log_dir, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(log_dir, 'news_aggregator.log')),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class RSSNewsAggregator:
    """RSS kaynaklarından haber toplama ve filtreleme sınıfı"""
    
    def __init__(self, config_path: str = "config/news_sources.json", 
                 watchlist_path: str = "config/watchlist.json"):
        """
        Args:
            config_path: Haber kaynakları config dosyası
            watchlist_path: Takip listesi config dosyası
        """
        self.config = self._load_config(config_path)
        self.watchlist = self._load_config(watchlist_path)
        self.news_cache = []
        self.last_update = None
        
        logger.info("RSS News Aggregator başlatıldı")
        
    def _load_config(self, path: str) -> dict:
        """Config dosyasını yükle"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Config yükleme hatası ({path}): {e}")
            return {}
    
    def fetch_rss_feed(self, feed_url: str, feed_name: str) -> List[Dict]:
        """
        Tek bir RSS feed'den haberleri çek
        
        Args:
            feed_url: RSS feed URL'i
            feed_name: Feed adı (loglama için)
            
        Returns:
            Haber listesi
        """
        try:
            logger.info(f"RSS feed çekiliyor: {feed_name}")
            feed = feedparser.parse(feed_url)
            
            news_items = []
            for entry in feed.entries:
                news_item = {
                    'source': feed_name,
                    'title': entry.get('title', ''),
                    'link': entry.get('link', ''),
                    'published': entry.get('published', ''),
                    'summary': entry.get('summary', ''),
                    'timestamp': datetime.now().isoformat()
                }
                news_items.append(news_item)
            
            logger.info(f"[OK] {feed_name}: {len(news_items)} haber toplandı")
            return news_items
            
        except Exception as e:
            logger.error(f"[ERROR] RSS feed hatası ({feed_name}): {e}")
            return []
    
    def fetch_all_feeds(self) -> List[Dict]:
        """
        Tüm RSS kaynaklarından haberleri çek
        
        Returns:
            Toplanan tüm haberler
        """
        all_news = []
        
        if 'news_sources' not in self.config:
            logger.error("Haber kaynakları config'de bulunamadı")
            return []
        
        rss_feeds = self.config['news_sources'].get('rss_feeds', {})
        
        # Her kategoriyi tara
        for category, feeds in rss_feeds.items():
            logger.info(f"=== {category.upper()} kategorisi işleniyor ===")
            
            for feed in feeds:
                feed_name = feed.get('name', 'Unknown')
                feed_url = feed.get('url', '')
                
                if not feed_url:
                    continue
                
                # Feed'i çek
                news_items = self.fetch_rss_feed(feed_url, feed_name)
                
                # Kategori ve öncelik bilgilerini ekle
                for item in news_items:
                    item['category'] = category
                    item['priority'] = feed.get('priority', 'low')
                    item['keywords'] = feed.get('keywords', [])
                
                all_news.extend(news_items)
                
                # Rate limiting - API'leri yormamak için
                time.sleep(1)
        
        self.news_cache = all_news
        self.last_update = datetime.now()
        
        logger.info(f"[OK] Toplam {len(all_news)} haber toplandı")
        return all_news
    
    def filter_relevant_news(self, news_items: List[Dict]) -> List[Dict]:
        """
        Watchlist'e göre ilgili haberleri filtrele
        
        Args:
            news_items: Tüm haberler
            
        Returns:
            Filtrelenmiş haberler
        """
        if not news_items:
            return []
        
        # Watchlist'ten tüm sembolleri al
        all_symbols = []
        stocks = self.watchlist.get('stocks', {})
        for category, symbols in stocks.items():
            all_symbols.extend(symbols)
        
        # Crypto sembolleri ekle
        crypto = self.watchlist.get('crypto', [])
        all_symbols.extend([c.replace('-USD', '') for c in crypto])
        
        relevant_news = []
        
        for item in news_items:
            title_lower = item['title'].lower()
            summary_lower = item['summary'].lower()
            content = f"{title_lower} {summary_lower}"
            
            # Sembol kontrolü
            for symbol in all_symbols:
                if symbol.lower() in content:
                    item['matched_symbol'] = symbol
                    item['relevance_score'] = self._calculate_relevance(item)
                    relevant_news.append(item)
                    break
            
            # Keyword kontrolü
            keywords = item.get('keywords', [])
            for keyword in keywords:
                if keyword.lower() in content:
                    if item not in relevant_news:
                        item['matched_keyword'] = keyword
                        item['relevance_score'] = self._calculate_relevance(item)
                        relevant_news.append(item)
                    break
        
        # Relevance score'a göre sırala
        relevant_news.sort(key=lambda x: x.get('relevance_score', 0), reverse=True)
        
        logger.info(f"[OK] {len(relevant_news)} ilgili haber filtrelendi")
        return relevant_news
    
    def _calculate_relevance(self, news_item: Dict) -> float:
        """
        Haberin önem skorunu hesapla
        
        Args:
            news_item: Haber öğesi
            
        Returns:
            0-100 arası skor
        """
        score = 0.0
        
        # Öncelik skoru
        priority_scores = {'high': 40, 'medium': 25, 'low': 10}
        score += priority_scores.get(news_item.get('priority', 'low'), 10)
        
        # Kategori skoru
        category_scores = {
            'commodities': 30, 'crypto': 25, 'general': 20,
            'tech': 15, 'market': 20
        }
        score += category_scores.get(news_item.get('category', ''), 10)
        
        # Sentiment keywords varsa +bonus
        sentiment_keywords = self.config.get('news_sources', {}).get('sentiment_keywords', {})
        content = f"{news_item['title']} {news_item['summary']}".lower()
        
        for pos_word in sentiment_keywords.get('positive', []):
            if pos_word.lower() in content:
                score += 5
        
        for neg_word in sentiment_keywords.get('negative', []):
            if neg_word.lower() in content:
                score += 5
        
        # High priority watchlist items
        priorities = self.watchlist.get('priorities', {})
        matched_symbol = news_item.get('matched_symbol', '').upper()
        
        if matched_symbol in priorities.get('high', []):
            score += 20
        elif matched_symbol in priorities.get('medium', []):
            score += 10
        
        return min(score, 100)
    
    def get_latest_news(self, hours: int = 24) -> List[Dict]:
        """
        Son X saatteki haberleri getir
        
        Args:
            hours: Kaç saat geriye bakılacak
            
        Returns:
            Filtrelenmiş haberler
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_news = [
            item for item in self.news_cache
            if datetime.fromisoformat(item['timestamp']) > cutoff_time
        ]
        
        return recent_news
    
    def save_news_to_file(self, news_items: List[Dict], filename: str = None):
        """
        Haberleri JSON dosyasına kaydet
        
        Args:
            news_items: Haber listesi
            filename: Kaydedilecek dosya adı
        """
        if filename is None:
            filename = f"data/news_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        try:
            Path(filename).parent.mkdir(parents=True, exist_ok=True)
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(news_items, f, indent=2, ensure_ascii=False)
            logger.info(f"[OK] Haberler kaydedildi: {filename}")
        except Exception as e:
            logger.error(f"[ERROR] Dosya kaydetme hatası: {e}")


def main():
    """Test fonksiyonu"""
    print("=== MIDAS PRO v5.0 - RSS News Aggregator ===\n")
    
    # Aggregator'ı başlat
    aggregator = RSSNewsAggregator()
    
    # Tüm haberleri çek
    print("[NEWS] Haberler toplanıyor...\n")
    all_news = aggregator.fetch_all_feeds()
    
    # İlgili haberleri filtrele
    print("\n🔍 İlgili haberler filtreleniyor...\n")
    relevant_news = aggregator.filter_relevant_news(all_news)
    
    # İlk 10 ilgili haberi göster
    print(f"\n[DATA] En İlgili {min(10, len(relevant_news))} Haber:\n")
    for i, news in enumerate(relevant_news[:10], 1):
        print(f"{i}. [{news.get('source', 'Unknown')}] {news['title']}")
        print(f"   Skor: {news.get('relevance_score', 0):.1f} | "
              f"Sembol: {news.get('matched_symbol', news.get('matched_keyword', 'N/A'))}")
        print(f"   Link: {news['link']}")
        print()
    
    # Dosyaya kaydet
    aggregator.save_news_to_file(relevant_news)
    
    print(f"\n[OK] İşlem tamamlandı. Toplam {len(relevant_news)} ilgili haber bulundu.")


if __name__ == "__main__":
    main()
