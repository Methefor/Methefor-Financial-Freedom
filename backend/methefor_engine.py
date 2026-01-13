"""
METHEFOR FİNANSAL ÖZGÜRLÜK v2.1
TAM ENTEGRE SİSTEM
+ AsyncIO Architecture
+ SQLite Database
+ Parallel Processing
"""

import sys
import os
import json
import asyncio
import aiohttp
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
from datetime import datetime
import time
import logging
from concurrent.futures import ThreadPoolExecutor

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
from src.ai.analyst import AIAnalyst
from src.trading.paper import PaperTrader
from src.database import init_db, get_session, NewsItem, TechnicalResult, Signal, Base, PortfolioItem

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


class NumpyEncoder(json.JSONEncoder):
    """NumPy types encoder for JSON"""
    def default(self, obj):
        import numpy as np
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        if isinstance(obj, np.bool_):
            return bool(obj)
        return super(NumpyEncoder, self).default(obj)


class MetheforFinancialFreedom:
    """METHEFOR FİNANSAL ÖZGÜRLÜK v2.1 - ASYNC ENGINE"""
    
    def __init__(self):
        logger.info("="*70)
        logger.info("METHEFOR FİNANSAL ÖZGÜRLÜK v2.1 başlatılıyor...")
        logger.info("="*70)
        
        config_dir = project_root / 'config'
        
        # Config yükle
        self.watchlist = self._load_config(config_dir / 'watchlist.json')
        self.trading_rules = self._load_config(config_dir / 'trading_rules.json')
        
        # Database Init
        logger.info("Veritabanı başlatılıyor...")
        self.db_engine = init_db('methefor.db')
        
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
        self.discovery_engine = DiscoveryEngine(config=self.watchlist.get('discovery', {}))
        self.ai_analyst = AIAnalyst()
        self.paper_trader = PaperTrader(lambda: get_session(self.db_engine))
        
        logger.info("[OK] Tüm modüller yüklendi! (Paper Trading Aktif)\n")
    
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
        
        # Auto-discovery
        if include_discoveries and self.watchlist.get('auto_discovery', {}).get('enabled', False):
            try:
                # Discovery is sync for now, keep it simple
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
        
        return list(set(symbols))

    async def collect_news_async(self) -> list:
        """Async ve paralel haber toplama"""
        logger.info("\n" + "="*70)
        logger.info("HABER TOPLAMA BAŞLATILIYOR (ASYNC)")
        logger.info("="*70)
        
        all_news = []
        
        async with aiohttp.ClientSession() as session:
            tasks = []
            
            # 1. Finnhub Market News
            tasks.append(self.finnhub_api.get_market_news_async(session))
            tasks.append(self.finnhub_api.get_market_news_async(session, category='crypto'))
            
            # 2. Priority Symbols News
            priority_symbols = self.watchlist.get('priorities', {}).get('high', [])[:5]
            for symbol in priority_symbols:
                tasks.append(self.finnhub_api.get_company_news_async(session, symbol))

            # Run all finnhub tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for res in results:
                if isinstance(res, list):
                    all_news.extend(res)
                elif isinstance(res, Exception):
                    logger.error(f"News fetch error: {res}")
        
        # 3. RSS Feeds (CPU bound/Blocking IO wrapper)
        # RSS runs in thread pool because feedparser is blocking
        loop = asyncio.get_event_loop()
        try:
            logger.info("RSS feed'ler taranıyor...")
            rss_news = await loop.run_in_executor(None, self.rss_aggregator.fetch_all_feeds)
            relevant_rss = await loop.run_in_executor(None, self.rss_aggregator.filter_relevant_news, rss_news)
            all_news.extend(relevant_rss)
        except Exception as e:
            logger.error(f"RSS error: {e}")

        logger.info(f"\n[OK] TOPLAM {len(all_news)} HABER TOPLANDI")
        return all_news

    async def analyze_sentiment_async(self, news_items: list) -> list:
        """Sentiment analizi (CPU bound - ThreadPool)"""
        logger.info("\n" + "="*70)
        logger.info("SENTIMENT ANALİZİ")
        logger.info("="*70)
        
        loop = asyncio.get_event_loop()
        try:
            # CPU intensive task, run in executor
            analyzed_news = await loop.run_in_executor(None, self.sentiment_analyzer.analyze_news_batch, news_items)
            logger.info(f"[OK] {len(analyzed_news)} haber analiz edildi")
            return analyzed_news
        except Exception as e:
            logger.error(f"Sentiment error: {e}")
            return []

    async def analyze_technical_async(self, symbols: list) -> dict:
        """Teknik analiz paralel (yfinance blocking olduğu için ThreadPool)"""
        logger.info("\n" + "="*70)
        logger.info("TEKNİK ANALİZ (PARALEL)")
        logger.info("="*70)

        technical_analysis = {}
        loop = asyncio.get_event_loop()
        
        # Max limit
        symbols = symbols[:20] 
        logger.info(f"{len(symbols)} sembol analiz edilecek...")
        
        async def analyze_single(symbol):
            try:
                # Run sync analyze_symbol in thread
                return await loop.run_in_executor(None, self.technical_analyzer.analyze_symbol, symbol)
            except Exception as e:
                logger.error(f"{symbol} analysis failed: {e}")
                return None

        # Create tasks
        tasks = [analyze_single(s) for s in symbols]
        results = await asyncio.gather(*tasks)
        
        for res in results:
            if res and 'error' not in res:
                technical_analysis[res['symbol']] = res
                logger.info(f"[OK] {res['symbol']}: {res['overall_score']:.1f}")
        
        return technical_analysis

    def generate_signals(self, analyzed_news: list, technical_analysis: dict) -> list:
        """Sinyal üretimi (Memory-bound, hızlı, sync kalabilir)"""
        # (Bu kod değişmedi, sadece çağırma şekli değişti)
        logger.info("\nSINYAL ÜRETİLİYOR...")
        
        sentiment_report = self.sentiment_analyzer.generate_sentiment_report(analyzed_news)
        signals = []
        
        weights = self.trading_rules.get('signal_generation', {}).get('weights', {})
        news_weight = weights.get('news_sentiment', 40) / 100
        tech_weight = weights.get('technical_analysis', 60) / 100
        
        for symbol, tech_data in technical_analysis.items():
            try:
                symbol_sentiment = sentiment_report['symbols'].get(symbol, {})
                sentiment_score = symbol_sentiment.get('overall_sentiment', 0)
                sentiment_confidence = symbol_sentiment.get('avg_confidence', 0)
                
                tech_score = tech_data.get('overall_score', 50)
                
                # Skor hesapla
                sentiment_scaled = (sentiment_score + 1) * 50
                combined_score = (sentiment_scaled * news_weight) + (tech_score * tech_weight)
                overall_confidence = (sentiment_confidence + tech_score) / 2
                
                # Karar
                if combined_score >= 75: decision = 'STRONG BUY'
                elif combined_score >= 60: decision = 'BUY'
                elif combined_score >= 40: decision = 'HOLD'
                elif combined_score >= 25: decision = 'SELL'
                else: decision = 'STRONG SELL'
                
                signal = {
                    'symbol': symbol,
                    'decision': decision,
                    'combined_score': combined_score,
                    'confidence': overall_confidence,
                    'sentiment_score': sentiment_score,
                    'technical_score': tech_score,
                    'reasons': tech_data['technical_signals']['signals'],
                    'timestamp': datetime.now()
                }
                signals.append(signal)
            except Exception as e:
                logger.error(f"Signal setup error {symbol}: {e}")
        
        signals.sort(key=lambda x: x['combined_score'], reverse=True)
        
        logger.info("[AI] Top 3 sinyal için açıklama üretiliyor...")
        for sig in signals[:3]:
            try:
                # Find related news (simple filter)
                related_news = [n for n in analyzed_news if sig['symbol'] in str(n)]
                explanation = self.ai_analyst.explain_signal(sig['symbol'], sig, related_news)
                sig['ai_explanation'] = explanation
                logger.info(f"[AI] {sig['symbol']} yorumlandı.")
            except Exception as e:
                logger.error(f"[AI] Error {sig['symbol']}: {e}")
                sig['ai_explanation'] = None
                
        return signals

    def save_to_db(self, news: list, technical: dict, signals: list):
        """Sonuçları veritabanına kaydet"""
        logger.info("\nVeritabanına kaydediliyor...")
        session = get_session(self.db_engine)
        try:
            # 1. Save News
            for n in news:
                link = n.get('link')
                # Check duplication first
                if session.query(NewsItem).filter_by(link=link).first():
                    continue

                item = NewsItem(
                    source=n.get('source'),
                    title=n.get('title'),
                    summary=n.get('summary'),
                    link=link,
                    published_date=datetime.now(), # Basitlik için
                    category=n.get('category'),
                    related_symbols=json.dumps(n.get('related_symbols', []), cls=NumpyEncoder),
                    sentiment_score=n.get('sentiment', {}).get('score', 0) if 'sentiment' in n else 0
                )
                session.add(item)
            
            # 2. Save Technical
            for sym, data in technical.items():
                tech = TechnicalResult(
                    symbol=sym,
                    price=data['price']['current'],
                    rsi=data['rsi']['value'],
                    macd_signal=data['macd']['signal'],
                    trend=data['moving_averages']['trend'],
                    overall_score=data['overall_score'],
                    details=json.dumps(data, cls=NumpyEncoder)
                )
                session.add(tech)
            
            # 3. Save Signals
            for sig in signals:
                s = Signal(
                    symbol=sig['symbol'],
                    decision=sig['decision'],
                    combined_score=sig['combined_score'],
                    confidence=sig['confidence'],
                    news_sentiment_score=sig['sentiment_score'],
                    technical_score=sig['technical_score'],
                    reasons=json.dumps(sig['reasons'], cls=NumpyEncoder),
                    ai_explanation=sig.get('ai_explanation')
                )
                session.add(s)
            
            session.commit()
            logger.info("[OK] Veritabanı kaydı başarılı.")

        except Exception as e:
            session.rollback()
            logger.error(f"DB Kayıt hatası: {e}")
        finally:
            session.close()

    async def run_full_cycle_async(self):
        """Asenkron Tam Döngü"""
        start_time = time.time()
        logger.info("\n" + "[ASYNC]"*35)
        logger.info("METHEFOR v2.1 (ASYNC) - BAŞLIYOR")
        logger.info("[ASYNC]"*35)
        
        # 1. Sembolleri belirle
        symbols = self.get_all_symbols()
        
        # 2. Parallel Execution (News & Technical)
        logger.info("\n>>> PARALEL İŞLEMLER BAŞLIYOR...")
        
        # Haber ve Teknik analizi aynı anda başlat
        news_task = asyncio.create_task(self.collect_news_async())
        tech_task = asyncio.create_task(self.analyze_technical_async(symbols))
        
        # Bekle
        news_results = await news_task
        technical_results = await tech_task
        
        # 3. Sentiment Analysis (News sonuçlarına bağlı)
        analyzed_news = await self.analyze_sentiment_async(news_results)
        
        # 4. Sinyal Üretimi
        signals = self.generate_signals(analyzed_news, technical_results)
        
        # 5. Telegram
        # (This is sync still, run in executor if needed, but it's IO bound so fast enough usually)
        if hasattr(self, 'telegram_bot'):
            # self.telegram_bot.send_alerts... (Implement wrapper if needed)
            pass 
        
        # 6. Sonuçları Kaydet
        self.save_to_db(analyzed_news, technical_results, signals)
        
        # 7. Paper Trading (Sanal İşlem)
        logger.info("🤖 Paper Trading işlemleri kontrol ediliyor...")
        self.paper_trader.execute_strategy(signals)
        
        # 8. Raporla
        self.print_summary(signals)
        
        elapsed = time.time() - start_time
        logger.info(f"\n[DONE] Döngü tamamlandı. Süre: {elapsed:.2f} saniye")

    def print_summary(self, signals):
        print("\n" + "="*70)
        print("EN İYİ SİNYALLER (v2.1 DB)")
        print("="*70)
        for s in signals[:5]:
            print(f"{s['symbol']}: {s['decision']} (Skor: {s['combined_score']:.1f})")

async def main_async():
    engine = MetheforFinancialFreedom()
    await engine.run_full_cycle_async()

def main():
    if os.name == 'nt':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
