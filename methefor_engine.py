"""
METHEFOR FİNANSAL ÖZGÜRLÜK v2.0
TAM ENTEGRE SİSTEM
+ Auto-Discovery System
+ 40+ Symbols Watchlist
+ Emoji-Free Professional Code
+ Full News + Sentiment + Technical Analysis
"""

import sys
import os
import json
from pathlib import Path
from datetime import datetime
import time
import logging
import numpy as np

# Proje root
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import modüller
from src.news.finnhub_api import FinnhubNewsAPI
from src.news.rss_aggregator import RSSNewsAggregator
from src.sentiment.analyzer import SentimentAnalyzer
from src.technical.analyzer import TechnicalAnalyzer
from src.notifications.telegram_bot import TelegramBot
from src.discovery.discovery_engine import DiscoveryEngine

# Logging setup
log_dir = project_root / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'methefor_engine.log', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class MetheforFinancialFreedom:
    """METHEFOR FİNANSAL ÖZGÜRLÜK v2.0 - TAM ENTEGRE SİSTEM"""
    
    def __init__(self):
        logger.info("="*70)
        logger.info("METHEFOR FİNANSAL ÖZGÜRLÜK v2.0 başlatılıyor...")
        logger.info("="*70)
        
        config_dir = project_root / 'config'
        
        # Config yükle
        self.watchlist = self._load_config(config_dir / 'watchlist.json')
        self.trading_rules = self._load_config(config_dir / 'trading_rules.json')
        
        # Modülleri başlat
        logger.info("\nModüller yükleniyor...")
        
        self.finnhub_api = FinnhubNewsAPI(config_path=str(config_dir / 'api_keys.json'))
        self.rss_aggregator = RSSNewsAggregator(
            config_path=str(config_dir / 'news_sources.json'),
            watchlist_path=str(config_dir / 'watchlist.json')
        )
        self.sentiment_analyzer = SentimentAnalyzer(config_path=str(config_dir / 'news_sources.json'))
        self.technical_analyzer = TechnicalAnalyzer()
        self.telegram_bot = TelegramBot(config_path=str(config_dir / 'api_keys.json'))
        
        # YENİ: Discovery Engine
        self.discovery_engine = DiscoveryEngine(config=self.watchlist.get('discovery', {}))
        
        logger.info("[OK] Tüm modüller yüklendi!\n")
    
    def _load_config(self, path: Path) -> dict:
        """Config dosyasını yükle"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Config yükleme hatası ({path}): {e}")
            return {}
    
    def get_all_symbols(self, include_discoveries: bool = True) -> list:
        """Watchlist + Discovery sembolleri"""
        symbols = []
        
        # Watchlist'ten sembolleri topla
        for category, stock_list in self.watchlist.get('stocks', {}).items():
            symbols.extend(stock_list)
        
        # Crypto ekle
        symbols.extend(self.watchlist.get('crypto', []))
        
        # Auto-discovery (YENİ!)
        if include_discoveries and self.watchlist.get('auto_discovery', {}).get('enabled', False):
            try:
                logger.info("\n[DISCOVERY] Yeni fırsatlar aranıyor...")
                discoveries = self.discovery_engine.discover_opportunities()
                
                if discoveries:
                    filtered = self.discovery_engine.filter_discoveries(
                        discoveries[:15],
                        min_volume=self.watchlist.get('discovery', {}).get('filters', {}).get('min_volume', 1000000)
                    )
                    
                    max_new = self.watchlist.get('auto_discovery', {}).get('max_new_symbols', 5)
                    symbols.extend(filtered[:max_new])
                    
                    logger.info(f"[OK] {len(filtered[:max_new])} keşfedilen sembol eklendi")
            except Exception as e:
                logger.error(f"[ERROR] Discovery hatası: {e}")
        
        return list(set(symbols))  # Unique
    
    def collect_news(self, use_finnhub: bool = True, use_rss: bool = True) -> list:
        """Tüm kaynaklardan haber topla"""
        logger.info("\n" + "="*70)
        logger.info("HABER TOPLAMA BAŞLATILIYOR")
        logger.info("="*70)
        
        all_news = []
        
        # 1. Finnhub API
        if use_finnhub:
            logger.info("\nFinnhub API'den haberler toplanıyor...")
            try:
                market_news = self.finnhub_api.get_market_news()
                all_news.extend(market_news)
                logger.info(f"[OK] Market haberleri: {len(market_news)}")
                
                # Öncelikli semboller için detaylı haber
                priority_symbols = self.watchlist.get('priorities', {}).get('high', [])[:10]
                
                for symbol in priority_symbols:
                    company_news = self.finnhub_api.get_company_news(symbol, days_back=3)
                    all_news.extend(company_news)
                    time.sleep(0.3)
                
                logger.info(f"[OK] Toplam Finnhub: {len(all_news)} haber")
            except Exception as e:
                logger.error(f"[ERROR] Finnhub hatası: {e}")
        
        # 2. RSS Feeds (25+ kaynak!)
        if use_rss:
            logger.info("\nRSS feed'lerden haberler toplanıyor (25+ kaynak)...")
            try:
                rss_news = self.rss_aggregator.fetch_all_feeds()
                relevant_rss = self.rss_aggregator.filter_relevant_news(rss_news)
                all_news.extend(relevant_rss)
                logger.info(f"[OK] RSS toplam: {len(relevant_rss)} ilgili haber")
            except Exception as e:
                logger.error(f"[ERROR] RSS hatası: {e}")
        
        logger.info(f"\n[OK] TOPLAM {len(all_news)} HABER TOPLANDI")
        return all_news
    
    def analyze_news_sentiment(self, news_items: list) -> list:
        """Haberlerin sentiment analizini yap"""
        logger.info("\n" + "="*70)
        logger.info("SENTIMENT ANALİZİ YAPILIYOR")
        logger.info("="*70)
        
        try:
            analyzed_news = self.sentiment_analyzer.analyze_news_batch(news_items)
            logger.info(f"[OK] {len(analyzed_news)} haber analiz edildi")
            return analyzed_news
        except Exception as e:
            logger.error(f"[ERROR] Sentiment analizi hatası: {e}")
            return []
    
    def analyze_technical(self, symbols: list = None, max_symbols: int = 15) -> dict:
        """Teknik analiz yap (optimized)"""
        logger.info("\n" + "="*70)
        logger.info("TEKNİK ANALİZ YAPILIYOR")
        logger.info("="*70)
        
        if symbols is None:
            symbols = self.get_all_symbols(include_discoveries=True)
        
        # Öncelik sırasına göre sırala
        priority_high = self.watchlist.get('priorities', {}).get('high', [])
        priority_medium = self.watchlist.get('priorities', {}).get('medium', [])
        
        # Önce high priority, sonra medium, sonra diğerleri
        sorted_symbols = []
        sorted_symbols.extend([s for s in priority_high if s in symbols])
        sorted_symbols.extend([s for s in priority_medium if s in symbols])
        sorted_symbols.extend([s for s in symbols if s not in sorted_symbols])
        
        # Sadece ilk max_symbols kadar analiz et
        symbols_to_analyze = sorted_symbols[:max_symbols]
        
        logger.info(f"[INFO] {len(symbols_to_analyze)} sembol analiz edilecek")
        
        technical_analysis = {}
        
        for i, symbol in enumerate(symbols_to_analyze, 1):
            try:
                logger.info(f"\n[{i}/{len(symbols_to_analyze)}] {symbol} analiz ediliyor...")
                analysis = self.technical_analyzer.analyze_symbol(symbol, period="3mo")
                
                if 'error' not in analysis:
                    technical_analysis[symbol] = analysis
                    logger.info(f"[OK] {symbol}: Skor {analysis.get('overall_score', 0)}/100")
                else:
                    logger.warning(f"[SKIP] {symbol}: {analysis.get('error', 'Unknown error')}")
                
                time.sleep(0.5)  # Rate limiting
                
            except Exception as e:
                logger.error(f"[ERROR] {symbol} analiz hatası: {e}")
                continue
        
        logger.info(f"\n[OK] {len(technical_analysis)} sembol teknik analizi tamamlandı")
        return technical_analysis
    
    def generate_combined_signals(self, analyzed_news: list, technical_analysis: dict) -> list:
        """Haber + Teknik analiz kombinasyonu ile sinyal üret"""
        logger.info("\n" + "="*70)
        logger.info("KOMBİNE SİNYAL ÜRETİMİ")
        logger.info("="*70)
        
        # Sentiment raporu oluştur
        sentiment_report = self.sentiment_analyzer.generate_sentiment_report(analyzed_news)
        signals = []
        
        # Ağırlıklar
        weights = self.trading_rules.get('signal_generation', {}).get('weights', {})
        news_weight = weights.get('news_sentiment', 40) / 100
        tech_weight = weights.get('technical_analysis', 60) / 100
        
        for symbol in technical_analysis.keys():
            try:
                # Sentiment verileri
                symbol_sentiment = sentiment_report['symbols'].get(symbol, {})
                sentiment_score = symbol_sentiment.get('overall_sentiment', 0)
                sentiment_confidence = symbol_sentiment.get('avg_confidence', 0)
                
                # Teknik veriler
                tech_data = technical_analysis[symbol]
                tech_score = tech_data.get('overall_score', 50)
                
                # Kombine hesaplama
                sentiment_scaled = (sentiment_score + 1) * 50  # -1 to 1 → 0 to 100
                combined_score = (sentiment_scaled * news_weight) + (tech_score * tech_weight)
                overall_confidence = (sentiment_confidence + tech_score) / 2
                
                # Karar mantığı
                if combined_score >= 75 and overall_confidence >= 65:
                    decision = 'STRONG BUY'
                elif combined_score >= 60 and overall_confidence >= 55:
                    decision = 'BUY'
                elif combined_score >= 40:
                    decision = 'HOLD'
                elif combined_score >= 25:
                    decision = 'SELL'
                else:
                    decision = 'STRONG SELL'
                
                # Sinyal objesi
                signal = {
                    'symbol': symbol,
                    'decision': decision,
                    'combined_score': combined_score,
                    'confidence': overall_confidence,
                    'sentiment': {
                        'score': sentiment_score,
                        'label': symbol_sentiment.get('sentiment_label', 'neutral'),
                        'confidence': sentiment_confidence,
                        'news_count': symbol_sentiment.get('news_count', 0)
                    },
                    'technical': {
                        'score': tech_score,
                        'decision': tech_data['technical_signals']['decision'],
                        'rsi': tech_data['rsi']['value'],
                        'trend': tech_data['moving_averages']['trend']
                    },
                    'price': tech_data.get('price', {}),
                    'timestamp': datetime.now().isoformat()
                }
                
                signals.append(signal)
                
            except Exception as e:
                logger.error(f"[ERROR] {symbol} sinyal üretimi hatası: {e}")
                continue
        
        # Skor'a göre sırala
        signals.sort(key=lambda x: x['combined_score'], reverse=True)
        logger.info(f"[OK] {len(signals)} kombine sinyal üretildi")
        
        return signals
    
    def send_telegram_alerts(self, signals: list, top_n: int = 5):
        """Önemli sinyalleri Telegram'a gönder"""
        logger.info("\n" + "="*70)
        logger.info("TELEGRAM BİLDİRİMLERİ GÖNDERİLİYOR")
        logger.info("="*70)
        
        # Sadece STRONG BUY/SELL ve yüksek confidence
        important_signals = [
            s for s in signals 
            if s['decision'] in ['STRONG BUY', 'STRONG SELL'] and s['confidence'] >= 60
        ]
        
        if not important_signals:
            logger.info("[INFO] Güçlü sinyal yok, bildirim gönderilmedi")
            return
        
        for signal in important_signals[:top_n]:
            try:
                logger.info(f"\n[TELEGRAM] {signal['symbol']} için bildirim gönderiliyor...")
                
                # Sebepleri topla
                reasons = []
                
                if signal['sentiment']['score'] > 0.5:
                    reasons.append(f"Pozitif haberler ({signal['sentiment']['news_count']} haber)")
                elif signal['sentiment']['score'] < -0.5:
                    reasons.append(f"Negatif haberler ({signal['sentiment']['news_count']} haber)")
                
                tech_signals = signal['technical']
                if tech_signals['rsi'] < 30:
                    reasons.append(f"RSI oversold ({tech_signals['rsi']:.1f})")
                elif tech_signals['rsi'] > 70:
                    reasons.append(f"RSI overbought ({tech_signals['rsi']:.1f})")
                
                reasons.append(f"Trend: {tech_signals['trend']}")
                
                # Telegram gönder
                self.telegram_bot.send_signal_alert(
                    symbol=signal['symbol'],
                    signal=signal['decision'],
                    sentiment_score=signal['sentiment']['score'],
                    technical_score=signal['technical']['score'],
                    confidence=signal['confidence'],
                    news_summary="",
                    reasons=reasons
                )
                
                logger.info(f"[OK] {signal['symbol']} bildirimi gönderildi")
                time.sleep(1)
                
            except Exception as e:
                logger.error(f"[ERROR] Telegram hatası: {e}")
        
        logger.info(f"\n[OK] {len(important_signals[:top_n])} bildirim gönderildi")
    
    def save_results(self, analyzed_news: list, technical_analysis: dict, signals: list):
        """Sonuçları kaydet"""
        
        def convert_numpy(obj):
            """NumPy tiplerini Python native'e çevir"""
            if isinstance(obj, (np.integer, int)):
                return int(obj)
            elif isinstance(obj, (np.floating, float)):
                return float(obj)
            elif isinstance(obj, (np.bool_, bool)):
                return bool(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {key: convert_numpy(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy(item) for item in obj]
            return obj
        
        # NumPy tiplerini çevir
        technical_analysis = convert_numpy(technical_analysis)
        signals = convert_numpy(signals)
        analyzed_news = convert_numpy(analyzed_news)
        
        data_dir = project_root / 'data'
        data_dir.mkdir(exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # 1. Haberler
        news_file = data_dir / f'news_{timestamp}.json'
        with open(news_file, 'w', encoding='utf-8') as f:
            json.dump(analyzed_news, f, indent=2, ensure_ascii=False)
        
        # 2. Teknik analiz
        tech_file = data_dir / f'technical_{timestamp}.json'
        with open(tech_file, 'w', encoding='utf-8') as f:
            json.dump(technical_analysis, f, indent=2, ensure_ascii=False)
        
        # 3. Sinyaller
        signals_file = data_dir / f'signals_{timestamp}.json'
        with open(signals_file, 'w', encoding='utf-8') as f:
            json.dump(signals, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n[OK] Sonuçlar kaydedildi:")
        logger.info(f"   Haberler: {news_file}")
        logger.info(f"   Teknik: {tech_file}")
        logger.info(f"   Sinyaller: {signals_file}")
    
    def run_full_cycle(self):
        """TAM DÖNGÜ: Discovery → Haber → Sentiment → Teknik → Sinyal → Telegram"""
        
        logger.info("\n" + "[MONEY]"*35)
        logger.info("METHEFOR v2.0 - TAM DÖNGÜ BAŞLATILIYOR")
        logger.info("[MONEY]"*35)
        
        # 1. Haber toplama
        news = self.collect_news(use_finnhub=True, use_rss=True)
        
        if not news:
            logger.warning("[WARNING] Haber toplanamadı!")
            return
        
        # 2. Sentiment analizi
        analyzed_news = self.analyze_news_sentiment(news)
        
        # 3. Teknik analiz (Discovery dahil!)
        symbols = self.get_all_symbols(include_discoveries=True)
        logger.info(f"\n[INFO] Toplam {len(symbols)} sembol (discovery dahil)")
        
        technical_analysis = self.analyze_technical(symbols, max_symbols=15)
        
        if not technical_analysis:
            logger.warning("[WARNING] Teknik analiz yapılamadı!")
            return
        
        # 4. Sinyal üretimi
        signals = self.generate_combined_signals(analyzed_news, technical_analysis)
        
        # 5. Telegram bildirimleri
        self.send_telegram_alerts(signals, top_n=5)
        
        # 6. Kaydetme
        self.save_results(analyzed_news, technical_analysis, signals)
        
        # 7. Özet rapor
        self.print_summary(signals)
        
        logger.info("\n" + "[OK]"*35)
        logger.info("TAM DÖNGÜ TAMAMLANDI!")
        logger.info("[OK]"*35 + "\n")
    
    def print_summary(self, signals: list):
        """Özet rapor yazdır"""
        
        print("\n" + "="*70)
        print("SINYAL ÖZETİ")
        print("="*70)
        
        buy_count = sum(1 for s in signals if 'BUY' in s['decision'])
        sell_count = sum(1 for s in signals if 'SELL' in s['decision'])
        hold_count = sum(1 for s in signals if s['decision'] == 'HOLD')
        
        print(f"\nToplam Sinyal: {len(signals)}")
        print(f"   AL: {buy_count}")
        print(f"   SAT: {sell_count}")
        print(f"   BEKLE: {hold_count}")
        
        print(f"\nEN İYİ 5 SİNYAL:")
        for i, signal in enumerate(signals[:5], 1):
            print(f"\n{i}. {signal['symbol']} - {signal['decision']}")
            print(f"   Kombine Skor: {signal['combined_score']:.1f}/100")
            print(f"   Güven: {signal['confidence']:.1f}%")
            print(f"   Sentiment: {signal['sentiment']['score']:+.2f} ({signal['sentiment']['label']})")
            print(f"   Teknik: {signal['technical']['score']:.0f}/100 ({signal['technical']['decision']})")
            print(f"   Fiyat: ${signal['price'].get('current', 0):.2f} ({signal['price'].get('change_1d', 0):+.2f}%)")
        
        print("\n" + "="*70)


def main():
    """Ana fonksiyon"""
    
    print("\n" + "[MONEY]"*35)
    print("METHEFOR FİNANSAL ÖZGÜRLÜK v2.0")
    print("Professional Trading Signal System")
    print("+ Auto-Discovery Engine")
    print("+ 40+ Symbols Watchlist")
    print("[MONEY]"*35 + "\n")
    
    engine = MetheforFinancialFreedom()
    engine.run_full_cycle()


if __name__ == "__main__":
    main()
