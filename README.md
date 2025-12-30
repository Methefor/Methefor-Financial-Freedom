# 💰 METHEFOR FİNANSAL ÖZGÜRLÜK v2.0

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.3+-green.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/status-production-brightgreen.svg)]()

**Professional AI-Powered Trading Signal System**

Otomatik haber toplama, sentiment analizi, teknik analiz ve sinyal üretimi ile 40+ sembolü takip eden gelişmiş trading platformu.

---

## 🚀 Özellikler

### ✅ v2.0 Yenilikleri (30 Aralık 2025)

- **📊 Gelişmiş Dashboard**: TradingView canlı grafikleri, detaylı sinyal modalları
- **🔍 Auto-Discovery**: Yeni fırsatları otomatik keşfeder (Yahoo Trending, Top Gainers, High Volume)
- **📰 25+ Haber Kaynağı**: Bloomberg, Reuters, CNBC, CoinDesk, TechCrunch ve daha fazlası
- **🤖 AI Sentiment Analizi**: 450+ haber üzerinde TextBlob sentiment analizi
- **📈 Teknik Analiz**: RSI, MACD, MA, Bollinger Bands, Volume analizi
- **🎯 Kombine Sinyal**: %40 sentiment + %60 teknik ağırlıklı karar sistemi
- **🔔 Telegram Bildirimleri**: STRONG BUY/SELL sinyalleri için otomatik bildirim
- **💻 Profesyonel Kod**: Emoji-free, Windows tam uyumlu, production-ready

---

## 📊 Takip Edilen Semboller (48 Adet)

### US Hisseler (34)
**Tech Giants**: NVDA, GOOG, GOOGL, MSFT, AMD, AMZN, AAPL, TSLA, META, AVGO, INTC, ORCL, ADBE  
**AI & Chips**: MRVL, LSCC, APP, SUPX  
**Emerging Tech**: PLTR, SYM, RKLB, HWM, OSCR  
**Automotive**: TSM, GM, BYDDY  
**Energy**: BE, NRG, ETN  
**Fintech**: MSTR, HOOD, SPOT, RDDT  
**Retail**: WMT, CVNA

### Emtialar (2)
SLV (Gümüş), GC=F (Altın)

### Türk Hisseleri (4)
THYAO.IS (Türk Hava Yolları), ASELS.IS (Aselsan), TUPRS.IS (Tüpraş), BIMAS.IS (BİM)

### Kripto (4)
BTC-USD, ETH-USD, SOL-USD, XRP-USD

### Discovery (5)
Sistem otomatik olarak yeni fırsatları keşfeder ve ekler

---

## 🎯 Sinyal Mantığı

### Karar Eşikleri:
- **STRONG BUY**: Kombine skor ≥75, Güven ≥65%
- **BUY**: Kombine skor ≥60, Güven ≥55%
- **HOLD**: Kombine skor ≥40
- **SELL**: Kombine skor ≥25
- **STRONG SELL**: Kombine skor <25

### Ağırlıklar:
- Sentiment: 40%
- Technical: 60%

### Örnek Hesaplama:
```
AMD:
  Sentiment: +0.80 (pozitif) → 90/100
  Technical: 60/100 (BUY)
  
  Kombine = (90 * 0.4) + (60 * 0.6)
          = 36 + 36
          = 72/100 → BUY
```

---

## ⚡ Hızlı Başlangıç

### 1. Kurulum

```bash
# Repository'yi klonla
git clone https://github.com/Methefor/Methefor-Financial-Freedom.git
cd Methefor-Financial-Freedom

# Bağımlılıkları yükle
pip install pandas numpy yfinance Flask Flask-CORS Flask-SocketIO feedparser requests textblob nltk python-telegram-bot python-dotenv
```

### 2. API Anahtarlarını Yapılandır

`config/api_keys.json` dosyasını oluştur:

```json
{
  "finnhub": {
    "api_key": "YOUR_FINNHUB_API_KEY"
  },
  "telegram": {
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID"
  },
  "newsapi": {
    "api_key": "YOUR_NEWSAPI_KEY"
  },
  "cryptopanic": {
    "auth_token": "YOUR_CRYPTOPANIC_TOKEN"
  }
}
```

**API Anahtarlarını Alma:**
- [Finnhub](https://finnhub.io/register) - Ücretsiz
- [NewsAPI](https://newsapi.org/register) - Ücretsiz (opsiyonel)
- [Telegram Bot](https://t.me/BotFather) - Ücretsiz
- [CryptoPanic](https://cryptopanic.com/developers/api/) - Ücretsiz (opsiyonel)

### 3. Çalıştır

```bash
# Ana motoru çalıştır (analiz + sinyal üretimi)
python methefor_engine.py

# Dashboard'u başlat (başka terminal)
cd dashboard
python app.py
```

### 4. Erişim

- **Dashboard**: http://localhost:5000
- **Telegram**: Botunuz otomatik bildirim gönderecek

---

## 📂 Proje Yapısı

```
Methefor_Finansal_Özgürlük/
├── config/
│   ├── api_keys.json           # API anahtarları (kendin oluştur)
│   ├── api_keys.example.json   # Örnek şablon
│   ├── watchlist.json          # 48 sembol + discovery ayarları
│   ├── trading_rules.json      # Sinyal kuralları
│   └── news_sources.json       # 25+ haber kaynağı
│
├── src/
│   ├── news/
│   │   ├── finnhub_api.py      # Finnhub API entegrasyonu
│   │   └── rss_aggregator.py   # 25+ RSS feed toplayıcı
│   ├── sentiment/
│   │   └── analyzer.py         # TextBlob sentiment analizi
│   ├── technical/
│   │   └── analyzer.py         # RSI, MACD, MA, Bollinger
│   ├── notifications/
│   │   └── telegram_bot.py     # Telegram bildirimleri
│   └── discovery/
│       └── discovery_engine.py # Yeni fırsat keşfi (YENİ!)
│
├── dashboard/
│   ├── app.py                  # Flask backend + SocketIO
│   └── templates/
│       └── index.html          # Modern UI + TradingView (YENİ!)
│
├── data/                       # JSON output dosyaları
│   ├── signals_*.json
│   ├── news_*.json
│   └── technical_*.json
│
├── logs/                       # Log dosyaları
├── methefor_engine.py          # Ana motor
├── requirements.txt
├── README.md
└── .gitignore
```

---

## 🔍 Auto-Discovery Sistemi

### Nasıl Çalışır?

1. **Yahoo Finance Trending**: Güncel trend sembolleri
2. **Top Gainers**: %5+ yükselen hisseler
3. **High Volume**: 2x+ hacim artışı olanlar
4. **Akıllı Filtreleme**:
   - Min hacim: 1M
   - Fiyat aralığı: $5-$1000
   - Market cap: >$100M

### Kullanım:

```python
from src.discovery.discovery_engine import DiscoveryEngine

engine = DiscoveryEngine()
discoveries = engine.discover_opportunities()

# Çıktı:
# [EKSO, NIO, BIDU, FTAI, META]
```

### Ayarlar (`config/watchlist.json`):

```json
"auto_discovery": {
  "enabled": true,
  "interval_hours": 6,
  "max_new_symbols": 5,
  "criteria": {
    "min_volume_surge": 3.0,
    "min_price_change": 7.0,
    "min_news_count": 3,
    "min_sentiment_score": 0.5
  }
}
```

---

## 📊 Dashboard Özellikleri

### Ana Ekran:
- 📈 **Real-time Stats**: Toplam/AL/SAT/Haber sayıları
- 🎯 **En İyi Sinyaller**: Top 10 sinyal kartları
- 📰 **Son Haberler**: Sentiment göstergeli haber akışı
- ⚡ **Auto-refresh**: 30 saniyede bir güncelleme

### Detaylı Modal (Hisseye Tıkla):
- 💰 Fiyat bilgileri (güncel, yüksek, düşük, hacim)
- 📊 Teknik analiz (RSI, MACD, trend, skor)
- 📰 Sentiment analiz (skor, label, haber sayısı)
- 🎯 Sinyal özeti (karar, güven, kombine skor)
- 📈 **TradingView Canlı Grafiği** (RSI + MACD)

### Animasyonlar:
- Anime.js ile kart girişleri
- Particle.js arka plan efektleri
- Sayı sayma animasyonları
- Glow efektleri (STRONG sinyaller)

---

## 🔔 Telegram Bildirimleri

### Kurulum:

1. [@BotFather](https://t.me/BotFather) ile bot oluştur
2. Bot token'ı al
3. Botunuza `/start` gönderin
4. Chat ID'nizi alın: https://api.telegram.org/bot<TOKEN>/getUpdates
5. `config/api_keys.json`'a ekleyin

### Bildirim Kriterleri:

- **STRONG BUY** veya **STRONG SELL** sinyali
- Güven ≥60%
- En fazla 5 bildirim/çalıştırma

### Örnek Bildirim:

```
🚀 STRONG BUY: MSTR

💰 $157.96 (+1.66%)
📊 Kombine: 78.5/100
🎯 Güven: 71.2%

📰 Sentiment: +0.82 (positive)
📈 Teknik: 75/100 (STRONG BUY)

Sebepler:
✓ Pozitif haberler (23 haber)
✓ RSI oversold (28.3)
✓ Trend: UPTREND

⏰ 30 Ara 2025 19:35
```

---

## 📈 Haber Kaynakları (25+)

### Genel Finans (12):
Bloomberg Markets, Reuters Business, CNBC, MarketWatch, Yahoo Finance, Investing.com, Business Insider, Seeking Alpha, Benzinga, Barron's, TheStreet, Motley Fool

### Emtialar (4):
Kitco Gold, Mining.com, OilPrice.com, Metals Daily

### Kripto (6):
CoinDesk, Cointelegraph, CryptoPanic, Bitcoin.com, Decrypt, The Block

### Teknoloji (4):
TechCrunch, The Verge, VentureBeat, Ars Technica

### Forex/Ekonomi (3):
FXStreet, DailyFX, TradingEconomics

---

## 🛠️ Geliştirme

### Test:

```bash
# Discovery test
python src/discovery/discovery_engine.py

# Sentiment test
python src/sentiment/analyzer.py

# Technical test
python src/technical/analyzer.py
```

### Log İnceleme:

```bash
tail -f logs/methefor_engine.log
```

### Yeni Sembol Ekleme:

`config/watchlist.json` düzenle:

```json
"stocks": {
  "custom": ["COIN", "RIOT", "MARA"]
}
```

---

## 📊 Performans Metrikleri

**Gerçek Test Sonuçları (30 Aralık 2025):**

| Metrik | Değer |
|--------|-------|
| Haber Toplama | 450 haber (3 saniye) |
| Sentiment Analizi | 450 analiz (1 saniye) |
| Teknik Analiz | 15 sembol (12 saniye) |
| Sinyal Üretimi | 15 sinyal (1 saniye) |
| **TOPLAM** | **~17 saniye** |

**Keşif Sonuçları:**
- EKSO: 67M hacim (10x normalin üzerinde!)
- NIO: 46M hacim
- BIDU, FTAI, META keşfedildi

---

## 🚨 Risk Uyarısı

**DİKKAT!** Bu yazılım sadece bilgilendirme amaçlıdır. Yatırım tavsiyesi değildir.

- Trading risk içerir
- Geçmiş performans gelecek garantisi değildir
- Kendi araştırmanızı yapın
- Kaybetmeyi göze alamayacağınız parayı yatırmayın
- Stop loss kullanın

**Önerilen Risk Yönetimi:**
- Pozisyon başına max %2 risk
- Günlük max %6 kayıp limiti
- Haftalık max %10 kayıp limiti
- Diversifikasyon (min 5 sembol)

---

## 🗺️ Roadmap

### v3.0 (Ocak 2026):
- [ ] AI Asistan Chatbot (Claude API)
- [ ] Watchlist yönetimi (dashboard'dan ekle/çıkar)
- [ ] Email bildirimleri
- [ ] Performans tracking (win rate, Sharpe ratio)

### v3.5 (Şubat 2026):
- [ ] Backtesting modülü
- [ ] Portfolio management
- [ ] Karşılaştırma modu (2-4 hisse)
- [ ] Haber sentiment timeline

### v4.0 (Mart 2026+):
- [ ] Mobile app (React Native)
- [ ] Social trading (leaderboard)
- [ ] Broker entegrasyonu (Interactive Brokers)
- [ ] Paper trading

---

## 📝 Değişiklik Geçmişi

### v2.0 (30 Aralık 2025)
- ✅ Auto-discovery sistemi eklendi
- ✅ TradingView grafik entegrasyonu
- ✅ Detaylı sinyal modalları
- ✅ Dashboard sayı düzeltmeleri
- ✅ 40+ sembol watchlist
- ✅ Emoji-free profesyonel kod
- ✅ Türk hisse desteği

### v1.0 (29 Aralık 2025)
- Temel haber toplama
- Sentiment analizi
- Teknik analiz
- Sinyal üretimi
- Telegram bildirimleri

---

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/YeniOzellik`)
3. Commit yapın (`git commit -m 'Yeni özellik: XYZ'`)
4. Push edin (`git push origin feature/YeniOzellik`)
5. Pull Request açın

---

## 📄 Lisans

MIT License - [LICENSE](LICENSE) dosyasına bakın

---

## 👤 İletişim

**Methefor**  
GitHub: [@Methefor](https://github.com/Methefor)  
Email: methefor@example.com

---

## 🙏 Teşekkürler

- [yfinance](https://github.com/ranaroussi/yfinance) - Market data
- [TextBlob](https://textblob.readthedocs.io/) - Sentiment analizi
- [TradingView](https://www.tradingview.com/) - Grafik widget'ları
- [Finnhub](https://finnhub.io/) - Haber API
- [Flask](https://flask.palletsprojects.com/) - Web framework

---

**💰 METHEFOR FİNANSAL ÖZGÜRLÜK - Empowering Financial Freedom**

⭐ Beğendiyseniz yıldız verin!
