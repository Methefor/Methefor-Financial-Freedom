"""
MIDAS PRO v6.0 - Telegram Bot Integration
Anlık sinyal bildirimleri ve komut sistemi
"""

import requests
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)


class TelegramBot:
    """Telegram bot ile bildirim ve komut sistemi"""
    
    def __init__(self, bot_token: str = None, chat_id: str = None, config_path: str = "config/api_keys.json"):
        """
        Args:
            bot_token: Telegram bot token
            chat_id: Telegram chat ID
            config_path: API keys config dosyası
        """
        if bot_token and chat_id:
            self.bot_token = bot_token
            self.chat_id = chat_id
        else:
            # Önce .env kontrol et
            import os
            self.bot_token = os.getenv('TELEGRAM_BOT_TOKEN', '')
            self.chat_id = os.getenv('TELEGRAM_CHAT_ID', '')
            
            # Eğer .env'de yoksa config'den oku
            if not self.bot_token or not self.chat_id:
                try:
                    with open(config_path, 'r', encoding='utf-8') as f:
                        config = json.load(f)
                        telegram_config = config.get('telegram', {})
                        self.bot_token = self.bot_token or telegram_config.get('bot_token', '')
                        self.chat_id = self.chat_id or telegram_config.get('chat_id', '')
                except Exception as e:
                    logger.error(f"Telegram config yüklenemedi: {e}")
        
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
        
        if not self.bot_token or self.bot_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            logger.warning("⚠️ Telegram bot token ayarlanmamış!")
            logger.info("📝 Bot oluşturmak için: @BotFather ile konuş")
        else:
            logger.info("[OK] Telegram Bot başlatıldı")
    
    def send_message(self, text: str, parse_mode: str = 'HTML') -> bool:
        """
        Telegram'a mesaj gönder
        
        Args:
            text: Mesaj metni
            parse_mode: HTML veya Markdown
            
        Returns:
            Başarılı ise True
        """
        if not self.bot_token or self.bot_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            logger.info(f"📱 [DEMO] Telegram mesajı: {text[:100]}...")
            return False
        
        try:
            url = f"{self.base_url}/sendMessage"
            payload = {
                'chat_id': self.chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            
            logger.info("[OK] Telegram mesajı gönderildi")
            return True
            
        except Exception as e:
            logger.error(f"Telegram mesaj hatası: {e}")
            return False
    
    def send_signal_alert(self, symbol: str, signal: str, sentiment_score: float,
                          technical_score: float, confidence: float, 
                          news_summary: str = "", reasons: List[str] = None) -> bool:
        """
        Trading sinyali bildirimi gönder
        
        Args:
            symbol: Hisse/kripto sembolü
            signal: BUY, SELL, HOLD
            sentiment_score: Haber sentiment skoru (-1 to +1)
            technical_score: Teknik analiz skoru (0-100)
            confidence: Genel güven skoru (0-100)
            news_summary: Haber özeti
            reasons: Sinyal nedenleri
            
        Returns:
            Başarılı ise True
        """
        # Emoji seçimi
        signal_emojis = {
            'STRONG BUY': '[ROCKET]',
            'BUY': '[UP]',
            'HOLD': '[PAUSE]',
            'WAIT': '[PAUSE]',
            'SELL': '[DOWN]',
            'STRONG SELL': '[DOWN]'
        }
        
        emoji = signal_emojis.get(signal, '•')
        
        # Mesaj oluştur
        message = f"""
{emoji} <b>{signal} SİNYALİ</b>

[CHART] <b>Sembol:</b> {symbol}
💭 <b>Sentiment:</b> {sentiment_score:+.2f} ({self._sentiment_label(sentiment_score)})
[UP] <b>Teknik Skor:</b> {technical_score:.0f}/100
🎯 <b>Güven:</b> {confidence:.0f}%

"""
        
        # Haber özeti
        if news_summary:
            message += f"[NEWS] <b>Son Haber:</b>\n{news_summary[:200]}...\n\n"
        
        # Nedenler
        if reasons:
            message += "💡 <b>Nedenler:</b>\n"
            for reason in reasons[:5]:
                message += f"   • {reason}\n"
        
        # Zaman
        message += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)
    
    def send_market_summary(self, top_gainers: List[Dict], top_losers: List[Dict],
                            total_signals: int, buy_signals: int, sell_signals: int) -> bool:
        """
        Piyasa özet raporu gönder
        
        Args:
            top_gainers: En çok yükselenler
            top_losers: En çok düşenler
            total_signals: Toplam sinyal sayısı
            buy_signals: AL sinyali sayısı
            sell_signals: SAT sinyali sayısı
            
        Returns:
            Başarılı ise True
        """
        message = f"""
[CHART] <b>PİYASA ÖZET RAPORU</b>

🎯 <b>Sinyal Özeti:</b>
   • Toplam: {total_signals}
   • AL: {buy_signals} [UP]
   • SAT: {sell_signals} [DOWN]

[+] <b>En Çok Yükselenler:</b>
"""
        
        for i, gainer in enumerate(top_gainers[:3], 1):
            message += f"   {i}. {gainer['symbol']}: {gainer['change']:+.2f}%\n"
        
        message += "\n[-] <b>En Çok Düşenler:</b>\n"
        
        for i, loser in enumerate(top_losers[:3], 1):
            message += f"   {i}. {loser['symbol']}: {loser['change']:+.2f}%\n"
        
        message += f"\n🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        
        return self.send_message(message)
    
    def send_portfolio_update(self, portfolio_value: float, daily_pnl: float,
                              total_pnl: float, open_positions: int) -> bool:
        """
        Portföy güncelleme bildirimi
        
        Args:
            portfolio_value: Portföy değeri
            daily_pnl: Günlük kar/zarar
            total_pnl: Toplam kar/zarar
            open_positions: Açık pozisyon sayısı
            
        Returns:
            Başarılı ise True
        """
        pnl_emoji = "[+]" if daily_pnl >= 0 else "[-]"
        
        message = f"""
💼 <b>PORTFÖY GÜNCELLEMESİ</b>

[MONEY] <b>Toplam Değer:</b> ${portfolio_value:,.2f}
{pnl_emoji} <b>Günlük P&L:</b> ${daily_pnl:,.2f} ({(daily_pnl/portfolio_value*100):+.2f}%)
[UP] <b>Toplam P&L:</b> ${total_pnl:,.2f}
[CHART] <b>Açık Pozisyon:</b> {open_positions}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return self.send_message(message)
    
    def send_risk_alert(self, alert_type: str, symbol: str, message: str) -> bool:
        """
        Risk uyarısı gönder
        
        Args:
            alert_type: STOP_LOSS, MAX_LOSS, etc.
            symbol: İlgili sembol
            message: Uyarı mesajı
            
        Returns:
            Başarılı ise True
        """
        alert_text = f"""
⚠️ <b>RİSK UYARISI</b>

🚨 <b>Tip:</b> {alert_type}
[CHART] <b>Sembol:</b> {symbol}

📝 <b>Mesaj:</b>
{message}

🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return self.send_message(alert_text)
    
    def _sentiment_label(self, score: float) -> str:
        """Sentiment skorunu label'a çevir"""
        if score > 0.5:
            return "Çok Pozitif"
        elif score > 0.3:
            return "Pozitif"
        elif score > -0.3:
            return "Nötr"
        elif score > -0.5:
            return "Negatif"
        else:
            return "Çok Negatif"
    
    def get_updates(self, offset: int = None, timeout: int = 30) -> List[Dict]:
        """
        Bot'a gelen mesajları al (komutlar için)
        
        Args:
            offset: Update offset
            timeout: Long polling timeout
            
        Returns:
            Update listesi
        """
        if not self.bot_token or self.bot_token == "YOUR_TELEGRAM_BOT_TOKEN_HERE":
            return []
        
        try:
            url = f"{self.base_url}/getUpdates"
            params = {
                'timeout': timeout
            }
            
            if offset:
                params['offset'] = offset
            
            response = requests.get(url, params=params, timeout=timeout+5)
            response.raise_for_status()
            
            data = response.json()
            return data.get('result', [])
            
        except Exception as e:
            logger.error(f"Telegram updates hatası: {e}")
            return []
    
    def process_command(self, command: str, args: List[str] = None) -> str:
        """
        Komut işle ve yanıt üret
        
        Args:
            command: Komut (örn: /start, /check, /help)
            args: Komut argümanları
            
        Returns:
            Yanıt mesajı
        """
        if command == '/start':
            return """
[ROCKET] <b>MIDAS PRO v6.0</b>

Hoş geldiniz! Kullanılabilir komutlar:

[CHART] /check [SEMBOL] - Sembol analizi
[NEWS] /news [SEMBOL] - Son haberler
[UP] /signals - Aktif sinyaller
💼 /portfolio - Portföy durumu
ℹ️ /help - Yardım

Örnek: /check AAPL
"""
        
        elif command == '/help':
            return """
ℹ️ <b>YARDIM</b>

<b>Komutlar:</b>
• /check AAPL - AAPL için tam analiz
• /news BTC - BTC haberlerini göster
• /signals - Tüm aktif sinyalleri listele
• /portfolio - Portföy özetini göster

<b>Otomatik Bildirimler:</b>
• GÜÇLÜ AL/SAT sinyalleri
• Risk uyarıları
• Portföy güncellemeleri
"""
        
        else:
            return f"[X] Bilinmeyen komut: {command}\n\nYardım için: /help"


def main():
    """Test fonksiyonu"""
    print("=== MIDAS PRO v6.0 - Telegram Bot Test ===\n")
    
    bot = TelegramBot()
    
    # Test 1: Basit mesaj
    print("📱 Test 1: Basit mesaj...")
    bot.send_message("[ROCKET] MIDAS PRO v6.0 Test Mesajı!")
    
    # Test 2: Sinyal bildirimi
    print("\n📱 Test 2: Sinyal bildirimi...")
    bot.send_signal_alert(
        symbol='AAPL',
        signal='STRONG BUY',
        sentiment_score=0.85,
        technical_score=78,
        confidence=82,
        news_summary="Apple announces breakthrough in AI chip technology with 50% performance boost",
        reasons=[
            "Pozitif haber momentum",
            "RSI oversold (32)",
            "MACD bullish crossover",
            "Volume spike (%180)"
        ]
    )
    
    # Test 3: Piyasa özeti
    print("\n📱 Test 3: Piyasa özeti...")
    bot.send_market_summary(
        top_gainers=[
            {'symbol': 'NVDA', 'change': 8.5},
            {'symbol': 'AMD', 'change': 6.2},
            {'symbol': 'TSLA', 'change': 4.1}
        ],
        top_losers=[
            {'symbol': 'META', 'change': -3.2},
            {'symbol': 'AAPL', 'change': -2.1},
            {'symbol': 'MSFT', 'change': -1.5}
        ],
        total_signals=15,
        buy_signals=8,
        sell_signals=4
    )
    
    print("\n[OK] Telegram bot test tamamlandı!")
    print("\n💡 Not: Gerçek mesajlar göndermek için:")
    print("   1. @BotFather ile bot oluştur")
    print("   2. Token'ı config/api_keys.json'a ekle")
    print("   3. Chat ID'ni al (@userinfobot)")


if __name__ == "__main__":
    main()
