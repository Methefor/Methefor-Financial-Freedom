"""
MIDAS PRO v5.0 - Sentiment Analyzer
NLP tabanlı haber duygu analizi ve skor hesaplama
"""

from typing import Dict, List, Tuple
import re
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """Haber sentiment analizi için NLP motoru"""
    
    def __init__(self, config_path: str = "config/news_sources.json"):
        """
        Args:
            config_path: Sentiment keywords içeren config dosyası
        """
        self.config = self._load_config(config_path)
        self.sentiment_keywords = self.config.get('sentiment_keywords', {})
        
        # Weighted keywords - bazı kelimeler daha önemli
        self.high_impact_words = {
            'positive': ['surge', 'soar', 'breakthrough', 'record high', 'strong demand', 'shortage'],
            'negative': ['crash', 'plunge', 'collapse', 'downgrade', 'warning', 'risk']
        }
        
        logger.info("Sentiment Analyzer başlatıldı")
    
    def _load_config(self, path: str) -> dict:
        """Config dosyasını yükle"""
        try:
            with open(path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Config yükleme hatası: {e}")
            return {}
    
    def analyze_text(self, text: str) -> Dict:
        """
        Metni analiz et ve sentiment skorunu hesapla
        
        Args:
            text: Analiz edilecek metin (başlık + özet)
            
        Returns:
            {
                'score': float (-1.0 to 1.0),
                'label': str ('positive', 'negative', 'neutral'),
                'confidence': float (0-100),
                'matched_keywords': dict
            }
        """
        text_lower = text.lower()
        
        # Keyword eşleşmelerini bul
        positive_matches = []
        negative_matches = []
        
        # Pozitif keyword'leri tara
        for keyword in self.sentiment_keywords.get('positive', []):
            keyword_lower = keyword.lower()
            # Tam kelime eşleşmesi veya içinde geçme
            if keyword_lower in text_lower or any(word in text_lower for word in keyword_lower.split()):
                # Ağırlık hesaplama
                if keyword in self.high_impact_words['positive']:
                    weight = 2.0
                else:
                    weight = 1.0
                positive_matches.append((keyword, weight))
        
        # Negatif keyword'leri tara
        for keyword in self.sentiment_keywords.get('negative', []):
            keyword_lower = keyword.lower()
            # Tam kelime eşleşmesi veya içinde geçme
            if keyword_lower in text_lower or any(word in text_lower for word in keyword_lower.split()):
                # Ağırlık hesaplama
                if keyword in self.high_impact_words['negative']:
                    weight = 2.0
                else:
                    weight = 1.0
                negative_matches.append((keyword, weight))
        
        # Skor hesaplama
        positive_score = sum(weight for _, weight in positive_matches)
        negative_score = sum(weight for _, weight in negative_matches)
        
        total_matches = len(positive_matches) + len(negative_matches)
        
        # Normalize edilmiş skor (-1.0 to 1.0)
        if positive_score + negative_score == 0:
            sentiment_score = 0.0
            label = 'neutral'
            confidence = 0
        else:
            sentiment_score = (positive_score - negative_score) / (positive_score + negative_score)
            
            # Label belirleme
            if sentiment_score > 0.3:
                label = 'positive'
            elif sentiment_score < -0.3:
                label = 'negative'
            else:
                label = 'neutral'
            
            # Güven skoru (0-100)
            confidence = min(100, total_matches * 15 + abs(sentiment_score) * 30)
        
        return {
            'score': round(sentiment_score, 3),
            'label': label,
            'confidence': round(confidence, 1),
            'matched_keywords': {
                'positive': [kw for kw, _ in positive_matches],
                'negative': [kw for kw, _ in negative_matches]
            },
            'positive_weight': positive_score,
            'negative_weight': negative_score
        }
    
    def analyze_news_item(self, news_item: Dict) -> Dict:
        """
        Tek bir haber öğesini analiz et
        
        Args:
            news_item: Haber dictionary'si
            
        Returns:
            Sentiment bilgisi eklenmiş haber
        """
        # Başlık ve özeti birleştir
        text = f"{news_item.get('title', '')} {news_item.get('summary', '')}"
        
        # Sentiment analizi yap
        sentiment = self.analyze_text(text)
        
        # Haber öğesine ekle
        news_item['sentiment'] = sentiment
        
        return news_item
    
    def analyze_news_batch(self, news_items: List[Dict]) -> List[Dict]:
        """
        Birden fazla haberi toplu analiz et
        
        Args:
            news_items: Haber listesi
            
        Returns:
            Sentiment eklenmiş haber listesi
        """
        analyzed_news = []
        
        for item in news_items:
            analyzed_item = self.analyze_news_item(item)
            analyzed_news.append(analyzed_item)
        
        logger.info(f"[OK] {len(news_items)} haber sentiment analizi tamamlandı")
        
        return analyzed_news
    
    def get_symbol_sentiment(self, news_items: List[Dict], symbol: str) -> Dict:
        """
        Belirli bir sembol için genel sentiment'i hesapla
        
        Args:
            news_items: Haber listesi
            symbol: Hisse sembolü (ör: 'SLV', 'AMD')
            
        Returns:
            {
                'symbol': str,
                'overall_sentiment': float,
                'positive_count': int,
                'negative_count': int,
                'neutral_count': int,
                'avg_confidence': float,
                'news_count': int
            }
        """
        symbol_news = [
            item for item in news_items
            if item.get('matched_symbol', '').upper() == symbol.upper()
        ]
        
        if not symbol_news:
            return {
                'symbol': symbol,
                'overall_sentiment': 0.0,
                'sentiment_label': 'neutral',
                'positive_count': 0,
                'negative_count': 0,
                'neutral_count': 0,
                'avg_confidence': 0.0,
                'news_count': 0
            }
        
        # Sentiment'leri topla
        sentiments = [item.get('sentiment', {}) for item in symbol_news]
        scores = [s.get('score', 0) for s in sentiments]
        confidences = [s.get('confidence', 0) for s in sentiments]
        
        # Sayım
        positive_count = sum(1 for s in sentiments if s.get('label') == 'positive')
        negative_count = sum(1 for s in sentiments if s.get('label') == 'negative')
        neutral_count = sum(1 for s in sentiments if s.get('label') == 'neutral')
        
        # Genel sentiment (ağırlıklı ortalama - confidence'a göre)
        if sum(confidences) > 0:
            weighted_sentiment = sum(
                score * conf for score, conf in zip(scores, confidences)
            ) / sum(confidences)
        else:
            weighted_sentiment = sum(scores) / len(scores) if scores else 0.0
        
        # Label belirleme
        if weighted_sentiment > 0.3:
            sentiment_label = 'positive'
        elif weighted_sentiment < -0.3:
            sentiment_label = 'negative'
        else:
            sentiment_label = 'neutral'
        
        return {
            'symbol': symbol,
            'overall_sentiment': round(weighted_sentiment, 3),
            'sentiment_label': sentiment_label,
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'avg_confidence': round(sum(confidences) / len(confidences), 1) if confidences else 0.0,
            'news_count': len(symbol_news),
            'recent_news': symbol_news[:3]  # Son 3 haber
        }
    
    def generate_sentiment_report(self, news_items: List[Dict], 
                                   symbols: List[str] = None) -> Dict:
        """
        Tüm semboller için sentiment raporu oluştur
        
        Args:
            news_items: Analiz edilmiş haberler
            symbols: Sembol listesi (None ise tüm semboller)
            
        Returns:
            Sentiment raporu
        """
        if symbols is None:
            # Tüm sembolleri bul
            symbols = list(set(
                item.get('matched_symbol', '') 
                for item in news_items 
                if item.get('matched_symbol')
            ))
        
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_news': len(news_items),
            'symbols': {}
        }
        
        for symbol in symbols:
            symbol_sentiment = self.get_symbol_sentiment(news_items, symbol)
            report['symbols'][symbol] = symbol_sentiment
        
        # En pozitif ve negatif sembolleri bul
        sorted_symbols = sorted(
            report['symbols'].items(),
            key=lambda x: x[1]['overall_sentiment'],
            reverse=True
        )
        
        report['most_positive'] = sorted_symbols[:5] if sorted_symbols else []
        report['most_negative'] = sorted_symbols[-5:] if len(sorted_symbols) >= 5 else []
        
        return report
    
    def print_sentiment_summary(self, sentiment_report: Dict):
        """
        Sentiment raporunu güzel formatta yazdır
        
        Args:
            sentiment_report: generate_sentiment_report() çıktısı
        """
        print("\n" + "="*60)
        print("[ANALYSIS] SENTIMENT ANALİZ RAPORU")
        print("="*60)
        print(f"Zaman: {sentiment_report['timestamp']}")
        print(f"Toplam Haber: {sentiment_report['total_news']}")
        print(f"Analiz Edilen Sembol: {len(sentiment_report['symbols'])}")
        
        print("\n[+] EN POZİTİF SEMBOLLER:")
        for symbol, data in sentiment_report.get('most_positive', [])[:5]:
            emoji = "[HIGH]" if data['overall_sentiment'] > 0.5 else "[POSITIVE]"
            print(f"{emoji} {symbol:6} | Skor: {data['overall_sentiment']:+.3f} | "
                  f"Güven: {data['avg_confidence']:.1f}% | "
                  f"Haber: {data['news_count']}")
        
        print("\n[-] EN NEGATİF SEMBOLLER:")
        for symbol, data in reversed(sentiment_report.get('most_negative', [])[-5:]):
            emoji = "⚠️" if data['overall_sentiment'] < -0.5 else "[DOWN]"
            print(f"{emoji} {symbol:6} | Skor: {data['overall_sentiment']:+.3f} | "
                  f"Güven: {data['avg_confidence']:.1f}% | "
                  f"Haber: {data['news_count']}")
        
        print("="*60 + "\n")


def main():
    """Test fonksiyonu"""
    print("=== MIDAS PRO v5.0 - Sentiment Analyzer Test ===\n")
    
    # Test metinleri
    test_texts = [
        "Silver prices surge as shortage concerns grow, analysts upgrade outlook",
        "AMD stock plunges after disappointing earnings, downgrade to sell",
        "Tesla maintains steady growth, mixed signals from analysts",
        "Bitcoin soars to record high as institutional demand increases",
        "Market crash fears as economic indicators show weakness"
    ]
    
    analyzer = SentimentAnalyzer()
    
    print("📝 Test Metinleri Analizi:\n")
    for i, text in enumerate(test_texts, 1):
        result = analyzer.analyze_text(text)
        
        emoji = "[+]" if result['label'] == 'positive' else "[-]" if result['label'] == 'negative' else "[=]"
        print(f"{i}. {emoji} [{result['label'].upper()}] Skor: {result['score']:+.3f} | Güven: {result['confidence']:.1f}%")
        print(f"   Metin: {text}")
        print(f"   Pozitif: {result['matched_keywords']['positive']}")
        print(f"   Negatif: {result['matched_keywords']['negative']}")
        print()


if __name__ == "__main__":
    main()
