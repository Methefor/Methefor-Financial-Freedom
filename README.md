# 💰 METHEFOR Financial Freedom Dashboard v3.0 ULTIMATE

<div align="center">

![Version](https://img.shields.io/badge/version-3.0-gold?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.8+-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/status-active-success?style=for-the-badge)

**Finansal Özgürlük Platformu - Profesyonel Trading Signal Dashboard**

[🌟 Özellikler](#-özellikler) • [📸 Ekran Görüntüleri](#-ekran-görüntüleri) • [⚡ Hızlı Başlangıç](#-hızlı-başlangıç) • [📚 Dokümantasyon](#-dokümantasyon)

**Repository:** [https://github.com/Methefor/Methefor-Financial-Freedom](https://github.com/Methefor/Methefor-Financial-Freedom)

</div>

---

## 📖 İçindekiler

- [Genel Bakış](#-genel-bakış)
- [Özellikler](#-özellikler)
- [Teknoloji Stack](#-teknoloji-stack)
- [Hızlı Başlangıç](#-hızlı-başlangıç)
- [Kurulum](#-kurulum)
- [Kullanım](#-kullanım)
- [API Endpoints](#-api-endpoints)
- [Konfigürasyon](#-konfigürasyon)
- [Proje Yapısı](#-proje-yapısı)
- [Changelog](#-changelog)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Lisans](#-lisans)
- [İletişim](#-iletişim)

---

## 🎯 Genel Bakış

**METHEFOR Financial Freedom Dashboard v3.0 ULTIMATE**, hisse senetleri, kripto paralar ve emtialar için gerçek zamanlı trading sinyalleri sunan profesyonel bir finansal analiz platformudur.

### 🌟 v3.0 Yenilikleri

#### 🎨 **Tasarım & UI/UX**

- ✨ Tamamen yeniden tasarlanmış modern arayüz
- 💫 Smooth animations ve transitions
- 🌈 Profesyonel gold tema (parlak, canlı renkler)
- 🎭 Glow effects ve shadow animations
- 📱 Geliştirilmiş responsive design
- 🎯 Hover effects ve loading skeletons

#### 🚀 **Performans & Teknik**

- ⚡ Optimize edilmiş CSS (tek stylesheet)
- 🧹 Temiz, modüler JavaScript kodu
- 🔧 Geliştirilmiş error handling
- 📊 Real-time WebSocket entegrasyonu
- 💾 Client-side caching
- 🔄 Auto-refresh optimizasyonu

#### 🔔 **Yeni Özellikler**

- 📈 Gelişmiş alert yönetim sistemi
- 🎨 Theme toggle (Dark/Light mode)
- 📊 İyileştirilmiş signal visualization
- 📰 Daha iyi news aggregation
- 🔍 Watchlist arama ve filtreleme
- 💬 Professional toast notifications

---

## ✨ Temel Özellikler

### 📊 **Trading Sinyalleri**

#### Teknik Analiz

- **RSI (Relative Strength Index)** - Aşırı alım/satım tespiti
- **MACD (Moving Average Convergence Divergence)** - Momentum göstergesi
- **Bollinger Bands** - Volatilite analizi
- **Moving Averages (SMA/EMA)** - Trend belirleme
- **Volume Analysis** - Hacim bazlı doğrulama
- **Trend Detection** - Otomatik trend tanıma

#### Sentiment Analizi

- 📰 **Multi-source news aggregation** - 420+ haber kaynağı
- 🤖 **AI-powered sentiment scoring** - Akıllı duygu analizi
- 📊 **Symbol-specific filtering** - Sembole özel filtreleme
- 🎯 **Confidence levels** - Güven seviyesi skorlaması

#### Signal Generation

- 🚀 **STRONG BUY** - Çok güçlü alım fırsatı
- 📈 **BUY** - Alım sinyali
- ⏸️ **HOLD** - Bekle
- 📉 **SELL** - Satış sinyali
- 🔴 **STRONG SELL** - Güçlü satış sinyali
- 🎯 **Combined Scoring** - Teknik 60% + Sentiment 40%

### 🔔 **Alert Management**

#### Alert Tipleri

- 📈 **Price Above** - Fiyat belirli seviyenin üstüne çıktığında
- 📉 **Price Below** - Fiyat belirli seviyenin altına düştüğünde
- 🔥 **RSI Oversold** - RSI < 30 (aşırı satım)
- ⚠️ **RSI Overbought** - RSI > 70 (aşırı alım)
- 🚨 **New Signal** - STRONG BUY/SELL sinyali oluştuğunda
- 📊 **Volume Spike** - Hacim 2x artışta

#### Bildirim Kanalları

- 📱 **Telegram** - Anlık bot bildirimleri
- 📧 **Email** (yakında)
- 🔔 **Browser Push** (yakında)

### 📊 **Watchlist Yönetimi**

#### Desteklenen Piyasalar

- 🇺🇸 **US Stocks** - NASDAQ, NYSE (AAPL, NVDA, AMD, TSLA, etc.)
- 🇹🇷 **Turkish Stocks** - BIST (THYAO.IS, GARAN.IS, ASELS.IS)
- ₿ **Cryptocurrencies** - BTC, ETH, SOL, XRP
- 🥇 **Commodities** - Gold (SLV), Oil, etc.

#### Özellikler

- 🔍 **Smart Search** - Hızlı sembol arama
- 🏷️ **Category Filtering** - Kategori bazlı gruplama
- ➕ **Quick Add/Remove** - Kolay ekleme/silme
- 📊 **Real-time Updates** - Canlı fiyat güncellemeleri
- 💾 **Persistent Storage** - Watchlist'iniz kaydediliyor

---

## 🛠️ Teknoloji Stack

### Backend

```python
Python 3.8+           # Core language
Flask 3.0+            # Web framework
Flask-SocketIO        # WebSocket support
yfinance              # Market data API
Pandas/NumPy          # Data processing & analysis
python-telegram-bot   # Telegram integration
feedparser            # RSS feed parser
BeautifulSoup4        # Web scraping
requests              # HTTP library
```

### Frontend

```javascript
HTML5/CSS3           # Modern web standards
JavaScript ES6+      # Vanilla JS (no frameworks)
Socket.IO Client     # Real-time communication
Particles.js         # Animated background
Anime.js             # Animation library
TradingView Widget   # Professional charts
```

### Data Sources

- **Market Data:** Yahoo Finance (yfinance)
- **News:** Finnhub API, NewsAPI, RSS Feeds
- **Crypto Data:** Binance, CoinGecko APIs
- **Turkish Stocks:** BIST real-time data feed

---

## ⚡ Hızlı Başlangıç

### 📋 Gereksinimler

- **Python:** 3.8 veya üzeri
- **pip:** Python package manager
- **Git:** Version control
- **Telegram Bot Token:** (isteğe bağlı) Bildirimler için

### 🚀 5 Dakikada Kurulum

```bash
# 1. Repository'yi klonla
git clone https://github.com/Methefor/Methefor-Financial-Freedom.git
cd Methefor-Financial-Freedom

# 2. Virtual environment oluştur
python -m venv venv

# Windows:
venv\Scripts\activate

# Linux/Mac:
source venv/bin/activate

# 3. Bağımlılıkları yükle
pip install -r requirements.txt

# 4. Konfigürasyon dosyasını oluştur
copy config.example.json config.json

# config.json dosyasını düzenle (API keys, tokens)

# 5. Dashboard'u başlat
cd dashboard
python app.py
```

**Tarayıcıda aç:** 🌐 **http://localhost:5000**

---

## 📦 Detaylı Kurulum

### 1️⃣ **Repository'yi Klonla**

```bash
git clone https://github.com/Methefor/Methefor-Financial-Freedom.git
cd Methefor-Financial-Freedom
```

### 2️⃣ **Virtual Environment Oluştur**

**Windows PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows CMD:**

```cmd
python -m venv venv
venv\Scripts\activate.bat
```

**Linux/Mac:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ **Bağımlılıkları Yükle**

```bash
# pip'i güncelle
pip install --upgrade pip

# Requirements'ları yükle
pip install -r requirements.txt
```

**Çıktı:**

```
Successfully installed Flask-3.0.0 Flask-SocketIO-5.3.5 yfinance-0.2.33 ...
```

### 4️⃣ **Konfigürasyon**

**config.example.json'u kopyala:**

```bash
copy config.example.json config.json
```

**config.json'u düzenle:**

```json
{
  "api_keys": {
    "finnhub": "YOUR_FINNHUB_API_KEY",
    "newsapi": "YOUR_NEWSAPI_KEY"
  },
  "telegram": {
    "bot_token": "YOUR_TELEGRAM_BOT_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "enabled": true
  },
  "watchlist": {
    "symbols": ["AAPL", "NVDA", "AMD", "BTC-USD", "THYAO.IS"]
  }
}
```

### 5️⃣ **API Keys Nasıl Alınır?**

#### **Finnhub API:**

1. 🌐 [finnhub.io](https://finnhub.io) adresine git
2. 📝 Ücretsiz hesap oluştur
3. 🔑 Dashboard'dan API key'ini kopyala
4. ✅ Free tier: 60 calls/minute

#### **NewsAPI:**

1. 🌐 [newsapi.org](https://newsapi.org) adresine git
2. 📝 Ücretsiz hesap oluştur (Developer plan)
3. 🔑 API key'ini kopyala
4. ✅ Free tier: 100 requests/day

#### **Telegram Bot:**

1. 📱 Telegram'ı aç
2. 🤖 [@BotFather](https://t.me/BotFather) ile konuş
3. 💬 `/newbot` komutu ile yeni bot oluştur
4. 📝 Bot adı ve username belirle
5. 🔑 Bot token'ı kopyala

**Chat ID nasıl bulunur:**

1. 🤖 [@userinfobot](https://t.me/userinfobot) ile konuş
2. 📋 Chat ID'ni kopyala

### 6️⃣ **İlk Çalıştırma**

```bash
cd dashboard
python app.py
```

**Başarılı çıktı:**

```
 * Running on http://0.0.0.0:5000
 * WebSocket server started
✓ Dashboard başlatıldı
✓ 30 sembol yüklendi
✓ Alert sistemi aktif
✓ Telegram bot bağlandı
```

**Tarayıcıda aç:**

```
http://localhost:5000
```

---

## 💻 Kullanım

### 🚀 **Dashboard Başlatma**

```bash
# Normal mode
python app.py

# Production mode
python app.py --prod

# Custom port
python app.py --port 8080

# Debug mode
python app.py --debug
```

### 📊 **Watchlist Yönetimi**

#### **Sembol Ekleme:**

1. Dashboard'da "➕ Sembol Ekle" butonuna tıkla
2. Sembol kodunu gir:
   - US stocks: `AAPL`, `NVDA`, `AMD`
   - Crypto: `BTC-USD`, `ETH-USD`
   - Turkish: `THYAO.IS`, `GARAN.IS`
3. "✅ Ekle" butonuna tıkla

#### **Sembol Silme:**

- Sembol kartı üzerindeki "×" butonuna tıkla
- Onaylama dialogunda "Evet" seç

#### **Filtreleme:**

- **Tümü** - Tüm sembolleri göster
- **US Stocks** - Sadece ABD hisseleri
- **TR Stocks** - Sadece Türk hisseleri
- **Crypto** - Sadece kripto paralar
- **Commodities** - Sadece emtialar

### 🔔 **Alert Oluşturma**

#### **Yeni Alert:**

1. "🔔 Alert Yönetimi" panelinde "➕ Alert Ekle"
2. **Sembol seç** (watchlist'inizden)
3. **Alert tipi seç:**
   - 📈 Fiyat Üstü → Threshold değeri gir
   - 📉 Fiyat Altı → Threshold değeri gir
   - 🔥 RSI Oversold → Otomatik (RSI<30)
   - ⚠️ RSI Overbought → Otomatik (RSI>70)
   - 🚨 Yeni Sinyal → Otomatik (STRONG BUY/SELL)
   - 📊 Hacim Artışı → Otomatik (Volume > 2x avg)
4. **Bildirim kanalı:** Telegram (default)
5. "✅ Alert Oluştur" tıkla

#### **Alert Yönetimi:**

- 🧪 **Test:** Test bildirimi gönder
- 🔔 **Aktif:** Alert'i etkinleştir
- 🔕 **Pasif:** Alert'i devre dışı bırak
- 🗑️ **Sil:** Alert'i kalıcı olarak sil

### 📈 **Signal Detayları**

**Sinyal kartına tıkladığında görürsün:**

- 💰 **Fiyat Bilgileri** - Güncel, yüksek, düşük, hacim
- 📊 **Teknik Analiz** - RSI, MACD, trend direction
- 📰 **Sentiment Analizi** - News sentiment score
- 📈 **TradingView Chart** - Canlı interaktif grafik
- 🤖 **AI Öneri** - Akıllı analiz ve tavsiye

---

## 🔌 API Endpoints

### **Summary**

```http
GET /api/summary
```

**Response:**

```json
{
  "total_signals": 30,
  "top_signals": [
    {
      "symbol": "AAPL",
      "decision": "STRONG BUY",
      "combined_score": 85.5,
      "confidence": 78.2,
      "price": {
        "current": 185.5,
        "change_1d": 2.5
      }
    }
  ],
  "news_stats": {
    "total": 420,
    "positive": 180,
    "negative": 120,
    "neutral": 120
  }
}
```

### **News**

```http
GET /api/news?limit=10&symbol=AAPL
```

**Response:**

```json
{
  "news": [
    {
      "title": "Apple announces new product",
      "source": "Reuters",
      "sentiment_label": "positive",
      "sentiment_score": 0.75,
      "symbols": ["AAPL"],
      "timestamp": "2025-01-05T10:30:00Z"
    }
  ]
}
```

### **Watchlist**

```http
GET /api/watchlist
POST /api/watchlist/add
POST /api/watchlist/remove
```

### **Alerts**

```http
GET /api/alerts
POST /api/alerts/add
POST /api/alerts/remove
POST /api/alerts/toggle
POST /api/alerts/test
```

**Detaylı API dokümantasyonu:** [API.md](docs/API.md)

---

## ⚙️ Konfigürasyon

### **config.json Detayları**

```json
{
  "api_keys": {
    "finnhub": "YOUR_KEY",
    "newsapi": "YOUR_KEY"
  },
  "telegram": {
    "bot_token": "YOUR_TOKEN",
    "chat_id": "YOUR_CHAT_ID",
    "enabled": true
  },
  "watchlist": {
    "symbols": ["AAPL", "NVDA", "AMD"],
    "auto_discovery": true,
    "max_symbols": 50
  },
  "alerts": {
    "enabled": true,
    "check_interval": 60,
    "max_alerts": 50
  },
  "dashboard": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false,
    "auto_refresh_interval": 30
  }
}
```

### **Environment Variables (.env)**

```bash
FINNHUB_API_KEY=your_finnhub_key
NEWSAPI_KEY=your_newsapi_key
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id
FLASK_ENV=production
PORT=5000
```

---

## 📁 Proje Yapısı

```
Methefor-Financial-Freedom/
├── dashboard/                  # Web dashboard
│   ├── app.py                 # Flask application
│   ├── templates/
│   │   └── index.html        # v3.0 ULTIMATE Dashboard
│   ├── static/
│   │   └── assets/
│   └── alerts.json           # Alert database
├── src/                       # Core modules
│   ├── signal_engine.py      # Signal generation
│   ├── news_aggregator.py    # News collection
│   ├── technical_analysis.py # Technical indicators
│   ├── sentiment_analyzer.py # Sentiment scoring
│   └── notification_manager.py # Notifications
├── data/                      # Data files
│   ├── watchlist.json        # Watchlist storage
│   └── cache/                # Cache directory
├── logs/                      # Application logs
├── docs/                      # Documentation
├── tests/                     # Test files
├── config.json               # Configuration
├── config.example.json       # Config template
├── requirements.txt          # Python dependencies
├── .gitignore               # Git ignore rules
├── LICENSE                   # MIT License
└── README.md                 # This file
```

---

## 📊 Changelog

### **v3.0.0** - 2025-01-05 🎉

#### ✨ New Features

- Complete UI/UX redesign with modern gold theme
- Smooth animations and transitions throughout
- Enhanced alert management system
- Improved signal visualization
- Better responsive design for all devices
- Performance tracking dashboard
- Theme toggle (Dark/Light mode)

#### 🛠️ Technical Improvements

- Clean, modular code structure
- Optimized CSS (single stylesheet)
- Enhanced JavaScript functionality
- Better error handling and logging
- Improved WebSocket integration
- Client-side caching

#### 📚 Documentation

- Comprehensive README.md
- Setup and installation guides
- API documentation
- Contributing guidelines
- Troubleshooting guide

#### 🔧 Configuration

- config.example.json template
- Updated requirements.txt
- Professional .gitignore
- Environment variables support

#### 📄 Legal

- MIT License
- Disclaimer and legal notices

### **v2.0.0** - 2024-12-15

- Initial public release
- Basic dashboard functionality
- Signal generation engine
- News aggregation
- Telegram notifications

---

## 🤝 Katkıda Bulunma

Katkılarınızı bekliyoruz! 🎉

### **Katkı Süreci:**

1. 🍴 **Fork** yapın
2. 🌿 Feature branch oluşturun
   ```bash
   git checkout -b feature/AmazingFeature
   ```
3. 💾 Değişikliklerinizi commit edin
   ```bash
   git commit -m '✨ Add: Amazing new feature'
   ```
4. 📤 Branch'inizi push edin
   ```bash
   git push origin feature/AmazingFeature
   ```
5. 🔀 **Pull Request** açın

### **Geliştirme Rehberi:**

- 🐍 Python için [PEP 8](https://www.python.org/dev/peps/pep-0008/) standartları
- 📜 JavaScript için [Airbnb Style Guide](https://github.com/airbnb/javascript)
- 📝 Commit mesajları için [Conventional Commits](https://www.conventionalcommits.org/)
- 🧪 Yeni özellikler için test yazın
- 📚 Dokümantasyonu güncel tutun

### **Commit Mesaj Formatı:**

```bash
✨ Add: Yeni özellik
🐛 Fix: Bug düzeltmesi
📝 Docs: Dokümantasyon
💄 Style: UI/styling değişiklikleri
♻️ Refactor: Code refactoring
⚡ Perf: Performance iyileştirmesi
✅ Test: Test ekleme/düzenleme
🔧 Chore: Bakım ve yapılandırma
```

---

## 🐛 Sorun Giderme

### **Yaygın Sorunlar:**

#### **1. Port zaten kullanımda**

```bash
# Farklı port kullan
python app.py --port 8080
```

#### **2. Module bulunamadı**

```bash
# Virtual environment'ı aktif et
venv\Scripts\activate

# Bağımlılıkları yeniden yükle
pip install -r requirements.txt --force-reinstall
```

#### **3. WebSocket bağlantı hatası**

```bash
# Firewall ayarlarını kontrol et
# Port 5000'i aç veya farklı port kullan
python app.py --port 8080
```

#### **4. Telegram bildirimleri çalışmıyor**

- ✅ Bot token'ını kontrol et
- ✅ Chat ID'nin doğruluğunu kontrol et
- ✅ Bot'u chat'e ekle ve `/start` komutu gönder
- ✅ config.json'da `telegram.enabled: true` olduğundan emin ol

#### **5. API rate limit**

- ⏱️ Finnhub: 60 calls/minute (free tier)
- ⏱️ NewsAPI: 100 requests/day (free tier)
- 💡 Premium hesaba yükselt veya cache kullan

**Detaylı sorun giderme:** [TROUBLESHOOTING.md](docs/TROUBLESHOOTING.md)

---

## 📊 Performans Metrikleri

- ⚡ **Dashboard Load Time:** < 2 saniye
- 🚀 **Signal Generation:** ~1 saniye (30 sembol için)
- 📡 **WebSocket Latency:** < 100ms
- 💾 **Memory Usage:** ~200MB (ortalama)
- 🖥️ **CPU Usage:** ~5-10% (idle state)
- 📊 **API Response Time:** < 500ms

---

## 🚀 Roadmap

### **v3.1** (Q2 2025)

- [ ] Email bildirim entegrasyonu
- [ ] Browser push notifications
- [ ] Performance tracking sistemi
- [ ] Backtesting özellikleri
- [ ] Excel/CSV export

### **v3.2** (Q3 2025)

- [ ] Multi-user support & authentication
- [ ] Portfolio tracking
- [ ] Advanced charting tools
- [ ] Mobile app (React Native)
- [ ] API rate limiting & caching

### **v4.0** (Q4 2025)

- [ ] Machine learning integration
- [ ] AI-powered price predictions
- [ ] Social trading features
- [ ] Premium subscription tier
- [ ] Public REST API

---

## 📜 Lisans

Bu proje **MIT License** altında lisanslanmıştır.

**Detaylar:** [LICENSE](LICENSE) dosyasına bakın.

```
MIT License

Copyright (c) 2025 Methefor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction...
```

---

## ⚠️ Yasal Uyarı & Disclaimer

### **ÖNEMLI - LÜTFEN DİKKATLE OKUYUN:**

Bu yazılım **yalnızca eğitim ve bilgilendirme amaçlıdır.**

#### **🚫 BU DEĞİLDİR:**

- ❌ Finansal tavsiye
- ❌ Yatırım tavsiyesi
- ❌ Profesyonel danışmanlık
- ❌ Garantili kazanç sistemi

#### **✅ BU BİR:**

- ✅ Eğitim aracı
- ✅ Teknik analiz öğrenme platformu
- ✅ Yazılım geliştirme projesi
- ✅ Açık kaynak demo uygulaması

#### **⚠️ RİSKLER:**

- Trading yüksek risk içerir
- Sermayenizin tamamını kaybedebilirsiniz
- Geçmiş performans gelecek sonuçların göstergesi değildir
- Piyasa koşulları değişkendir
- Duygusal kararlar zararlı olabilir

#### **📋 TAVSİYELERİMİZ:**

- 👨‍💼 Profesyonel finansal danışman ile görüşün
- 📚 Kendi araştırmanızı yapın
- 💰 Sadece kaybetmeyi göze alabileceğiniz para ile işlem yapın
- 🎯 Risk yönetimi stratejisi kullanın
- 📊 Stop-loss emirleri koymayı unutmayın
- 🧘 Disiplinli ve sabırlı olun

#### **🛡️ SORUMLULUK REDDİ:**

Bu yazılımın geliştiricileri ve katkıda bulunanlar:

- Finansal kayıplardan sorumlu değildir
- Yatırım kararlarınızdan sorumlu değildir
- Yazılım hatalarından kaynaklanan zararlardan sorumlu değildir
- Herhangi bir garanti vermemektedir

**USE AT YOUR OWN RISK / KENDİ RİSKİNİZLE KULLANIN**

---

## 📞 İletişim & Destek

### **Geliştirici:**

- 👤 **Name:** Methefor Development Team
- 🌐 **GitHub:** [@Methefor](https://github.com/Methefor)
- 📧 **Email:** methefor@proton.me
- 💬 **Telegram:** [@Midas_Sinyal_Bot](https://t.me/Midas_Sinyal_Bot)

### **Project Links:**

- 📦 **Repository:** [https://github.com/Methefor/Methefor-Financial-Freedom](https://github.com/Methefor/Methefor-Financial-Freedom)
- 📚 **Documentation:** [https://github.com/Methefor/Methefor-Financial-Freedom/wiki](https://github.com/Methefor/Methefor-Financial-Freedom/wiki)
- 🐛 **Issues:** [https://github.com/Methefor/Methefor-Financial-Freedom/issues](https://github.com/Methefor/Methefor-Financial-Freedom/issues)
- 💬 **Discussions:** [https://github.com/Methefor/Methefor-Financial-Freedom/discussions](https://github.com/Methefor/Methefor-Financial-Freedom/discussions)

### **Destek:**

- 📖 [FAQ](docs/FAQ.md) - Sık sorulan sorular
- 🔧 [Troubleshooting Guide](docs/TROUBLESHOOTING.md) - Sorun giderme
- 💡 [Feature Requests](https://github.com/Methefor/Methefor-Financial-Freedom/issues/new?template=feature_request.md)
- 🐛 [Bug Reports](https://github.com/Methefor/Methefor-Financial-Freedom/issues/new?template=bug_report.md)

---

## 🙏 Teşekkürler

Bu projenin geliştirilmesinde kullanılan açık kaynak projelere teşekkür ederiz:

### **Core Technologies:**

- [Flask](https://flask.palletsprojects.com/) - Python web framework
- [Socket.IO](https://socket.io/) - Real-time bidirectional communication
- [yfinance](https://github.com/ranaroussi/yfinance) - Yahoo Finance market data
- [Pandas](https://pandas.pydata.org/) - Data analysis library
- [NumPy](https://numpy.org/) - Scientific computing

### **Frontend Libraries:**

- [Particles.js](https://vincentgarreau.com/particles.js/) - Background animations
- [Anime.js](https://animejs.com/) - Animation library
- [TradingView](https://www.tradingview.com/) - Financial charts

### **Integrations:**

- [Python Telegram Bot](https://python-telegram-bot.org/) - Telegram API wrapper
- [Finnhub](https://finnhub.io/) - Financial news API
- [NewsAPI](https://newsapi.org/) - News aggregation

### **Special Thanks:**

- 🌟 Open source community
- 💡 Contributors and testers
- 📚 Documentation writers
- 🐛 Bug reporters
- ⭐ Star gazers

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=Methefor/Methefor-Financial-Freedom&type=Date)](https://star-history.com/#Methefor/Methefor-Financial-Freedom&Date)

---

## 📈 GitHub Stats

![GitHub stars](https://img.shields.io/github/stars/Methefor/Methefor-Financial-Freedom?style=social)
![GitHub forks](https://img.shields.io/github/forks/Methefor/Methefor-Financial-Freedom?style=social)
![GitHub watchers](https://img.shields.io/github/watchers/Methefor/Methefor-Financial-Freedom?style=social)
![GitHub issues](https://img.shields.io/github/issues/Methefor/Methefor-Financial-Freedom)
![GitHub pull requests](https://img.shields.io/github/issues-pr/Methefor/Methefor-Financial-Freedom)
![GitHub last commit](https://img.shields.io/github/last-commit/Methefor/Methefor-Financial-Freedom)
![GitHub repo size](https://img.shields.io/github/repo-size/Methefor/Methefor-Financial-Freedom)
![GitHub language count](https://img.shields.io/github/languages/count/Methefor/Methefor-Financial-Freedom)
![GitHub top language](https://img.shields.io/github/languages/top/Methefor/Methefor-Financial-Freedom)

---

<div align="center">

**Made with ❤️ and ☕ by Methefor Development Team**

⭐ **Bu projeyi beğendiyseniz yıldız vermeyi unutmayın!**

🚀 **Happy Trading! (But remember: DYOR - Do Your Own Research)**

[⬆ Başa Dön](#-methefor-financial-freedom-dashboard-v30-ultimate)

---

**© 2025 Methefor. All rights reserved.**

_Bu README.md dosyası sürekli güncellenmektedir. Son güncelleme: 2025-01-05_

</div>
