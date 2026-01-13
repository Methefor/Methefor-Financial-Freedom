"""
Notification Manager - Methefor Finansal Özgürlük
Email, Telegram ve Browser bildirimleri gönderir
"""

import json
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
import requests
from datetime import datetime

class NotificationManager:
    def __init__(self, base_dir, socketio=None):
        self.base_dir = Path(base_dir)
        self.socketio = socketio
        
        # Email config yükle
        self.email_config = self.load_email_config()
        
        # Telegram config yükle
        self.telegram_config = self.load_telegram_config()
    
    def load_email_config(self):
        """Email konfigürasyonunu yükle"""
        try:
            config_file = self.base_dir / 'config' / 'email_config.json'
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print("⚠️ email_config.json bulunamadı")
                return None
        except Exception as e:
            print(f"Email config yükleme hatası: {e}")
            return None
    
    def load_telegram_config(self):
        """Telegram konfigürasyonunu yükle"""
        try:
            # telegram_config.json varsa onu kullan
            config_file = self.base_dir / 'config' / 'telegram_config.json'
            if config_file.exists():
                with open(config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            # Yoksa .env'den oku
            env_file = self.base_dir / '.env'
            if env_file.exists():
                config = {}
                with open(env_file, 'r') as f:
                    for line in f:
                        if line.startswith('TELEGRAM_BOT_TOKEN'):
                            config['bot_token'] = line.split('=')[1].strip()
                        elif line.startswith('TELEGRAM_CHAT_ID'):
                            config['chat_id'] = line.split('=')[1].strip()
                
                if config:
                    return config
            
            print("⚠️ Telegram config bulunamadı")
            return None
            
        except Exception as e:
            print(f"Telegram config yükleme hatası: {e}")
            return None
    
    def send_telegram(self, alert, signal):
        """Telegram bildirimi gönder"""
        try:
            if not self.telegram_config:
                print("⚠️ Telegram config yok, bildirim gönderilemedi")
                return False
            
            bot_token = self.telegram_config.get('bot_token')
            chat_id = self.telegram_config.get('chat_id')
            
            if not bot_token or not chat_id:
                print("⚠️ Telegram bot_token veya chat_id eksik")
                return False
            
            # Mesaj oluştur
            message = self.format_telegram_message(alert, signal)
            
            # Telegram API
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
            
            if response.status_code == 200:
                print(f"✓ Telegram bildirimi gönderildi: {alert['symbol']}")
                return True
            else:
                print(f"✗ Telegram API hatası: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"Telegram gönderme hatası: {e}")
            return False
    
    def format_telegram_message(self, alert, signal):
        """Telegram mesajını formatla"""
        try:
            symbol = alert['symbol']
            alert_type = alert['type']
            
            # Başlık
            message = f"🚨 <b>ALERT: {symbol}</b>\n\n"
            
            # Alert tipi açıklaması
            if alert_type == 'price_above':
                target = alert['condition']['price']
                current = signal['price']['current']
                message += f"💰 Fiyat hedef üzerine çıktı!\n"
                message += f"Hedef: ${target:.2f}\n"
                message += f"Güncel: ${current:.2f}\n"
            
            elif alert_type == 'price_below':
                target = alert['condition']['price']
                current = signal['price']['current']
                message += f"📉 Fiyat hedef altına düştü!\n"
                message += f"Hedef: ${target:.2f}\n"
                message += f"Güncel: ${current:.2f}\n"
            
            elif alert_type == 'rsi_below':
                target = alert['condition']['rsi']
                current = signal['technical']['rsi']
                message += f"🔥 RSI oversold!\n"
                message += f"Hedef: {target}\n"
                message += f"Güncel: {current:.1f}\n"
            
            elif alert_type == 'rsi_above':
                target = alert['condition']['rsi']
                current = signal['technical']['rsi']
                message += f"⚠️ RSI overbought!\n"
                message += f"Hedef: {target}\n"
                message += f"Güncel: {current:.1f}\n"
            
            elif alert_type == 'new_signal':
                decision = signal['decision']
                message += f"📊 Yeni Sinyal: <b>{decision}</b>\n"
                message += f"Güven: {signal['confidence']:.1f}%\n"
            
            # Ek bilgiler
            message += f"\n📈 Karar: {signal.get('decision', 'N/A')}\n"
            message += f"💯 Skor: {signal.get('combined_score', 0):.0f}/100\n"
            
            message += f"\n🕐 {datetime.now().strftime('%d.%m.%Y %H:%M')}"
            
            return message
            
        except Exception as e:
            print(f"Telegram mesaj formatla hatası: {e}")
            return f"🚨 ALERT: {alert['symbol']}"
    
    def send_email(self, alert, signal):
        """Email bildirimi gönder"""
        try:
            if not self.email_config:
                print("⚠️ Email config yok, bildirim gönderilemedi")
                return False
            
            smtp_server = self.email_config.get('smtp_server')
            smtp_port = self.email_config.get('smtp_port')
            email = self.email_config.get('email')
            app_password = self.email_config.get('app_password')
            recipient = self.email_config.get('recipient')
            
            if not all([smtp_server, smtp_port, email, app_password, recipient]):
                print("⚠️ Email config eksik")
                return False
            
            # Email oluştur
            msg = MIMEMultipart('alternative')
            msg['Subject'] = f"🚨 METHEFOR ALERT: {alert['symbol']}"
            msg['From'] = email
            msg['To'] = recipient
            
            # HTML içerik
            html = self.format_email_html(alert, signal)
            msg.attach(MIMEText(html, 'html'))
            
            # Gönder
            with smtplib.SMTP_SSL(smtp_server, smtp_port) as smtp:
                smtp.login(email, app_password)
                smtp.send_message(msg)
            
            print(f"✓ Email gönderildi: {alert['symbol']}")
            return True
            
        except Exception as e:
            print(f"Email gönderme hatası: {e}")
            return False
    
    def format_email_html(self, alert, signal):
        """Email HTML içeriği"""
        try:
            symbol = alert['symbol']
            alert_type = alert['type']
            decision = signal.get('decision', 'N/A')
            confidence = signal.get('confidence', 0)
            
            # Alert tipi açıklaması
            alert_desc = ""
            if alert_type == 'price_above':
                target = alert['condition']['price']
                current = signal['price']['current']
                alert_desc = f"Fiyat ${target:.2f} hedefinin üzerine çıktı! Güncel: ${current:.2f}"
            
            elif alert_type == 'price_below':
                target = alert['condition']['price']
                current = signal['price']['current']
                alert_desc = f"Fiyat ${target:.2f} hedefinin altına düştü! Güncel: ${current:.2f}"
            
            elif alert_type == 'rsi_below':
                target = alert['condition']['rsi']
                current = signal['technical']['rsi']
                alert_desc = f"RSI {target} seviyesinin altına düştü (Oversold)! Güncel: {current:.1f}"
            
            elif alert_type == 'new_signal':
                alert_desc = f"Yeni {decision} sinyali oluştu!"
            
            html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <style>
                    body {{ font-family: Arial, sans-serif; background: #f4f4f4; }}
                    .container {{ max-width: 600px; margin: 20px auto; background: white; padding: 30px; border-radius: 10px; }}
                    .header {{ background: linear-gradient(135deg, #0a0e27 0%, #1e293b 100%); color: #FFD700; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ padding: 20px; }}
                    .alert-box {{ background: #fff3cd; border-left: 5px solid #ffc107; padding: 15px; margin: 20px 0; }}
                    .stats {{ display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0; }}
                    .stat {{ background: #f8f9fa; padding: 15px; border-radius: 8px; text-align: center; }}
                    .stat-label {{ color: #6c757d; font-size: 0.9em; }}
                    .stat-value {{ font-size: 1.5em; font-weight: bold; color: #0a0e27; }}
                    .footer {{ text-align: center; color: #6c757d; font-size: 0.85em; margin-top: 20px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🚨 METHEFOR ALERT</h1>
                        <h2>{symbol}</h2>
                    </div>
                    
                    <div class="content">
                        <div class="alert-box">
                            <strong>⚠️ Alert Tetiklendi:</strong><br>
                            {alert_desc}
                        </div>
                        
                        <div class="stats">
                            <div class="stat">
                                <div class="stat-label">Karar</div>
                                <div class="stat-value">{decision}</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Güven</div>
                                <div class="stat-value">{confidence:.1f}%</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">Fiyat</div>
                                <div class="stat-value">${signal['price']['current']:.2f}</div>
                            </div>
                            <div class="stat">
                                <div class="stat-label">RSI</div>
                                <div class="stat-value">{signal['technical']['rsi']:.1f}</div>
                            </div>
                        </div>
                        
                        <p style="text-align: center; margin-top: 30px;">
                            <a href="http://localhost:5000" style="background: #FFD700; color: #0a0e27; padding: 12px 30px; text-decoration: none; border-radius: 5px; font-weight: bold;">
                                📊 Dashboard'a Git
                            </a>
                        </p>
                    </div>
                    
                    <div class="footer">
                        <p>METHEFOR Finansal Özgürlük</p>
                        <p>{datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            return html
            
        except Exception as e:
            print(f"Email HTML formatla hatası: {e}")
            return f"<h1>ALERT: {alert['symbol']}</h1>"
    
    def send_browser_notification(self, alert, signal):
        """Browser notification gönder (SocketIO ile)"""
        try:
            if not self.socketio:
                print("⚠️ SocketIO yok, browser notification gönderilemedi")
                return False
            
            notification_data = {
                'alert': {
                    'id': alert['id'],
                    'symbol': alert['symbol'],
                    'type': alert['type'],
                    'message': self.format_browser_message(alert, signal)
                },
                'signal': {
                    'symbol': signal['symbol'],
                    'decision': signal['decision'],
                    'confidence': signal['confidence'],
                    'price': signal['price']['current']
                },
                'timestamp': datetime.now().isoformat()
            }
            
            # SocketIO emit
            self.socketio.emit('alert_triggered', notification_data)
            
            print(f"✓ Browser notification gönderildi: {alert['symbol']}")
            return True
            
        except Exception as e:
            print(f"Browser notification hatası: {e}")
            return False
    
    def format_browser_message(self, alert, signal):
        """Browser notification mesajı"""
        try:
            symbol = alert['symbol']
            alert_type = alert['type']
            
            if alert_type == 'price_above':
                target = alert['condition']['price']
                current = signal['price']['current']
                return f"{symbol}: ${current:.2f} (hedef: ${target:.2f})"
            
            elif alert_type == 'rsi_below':
                rsi = signal['technical']['rsi']
                return f"{symbol}: RSI {rsi:.1f} (Oversold!)"
            
            elif alert_type == 'new_signal':
                decision = signal['decision']
                return f"{symbol}: Yeni {decision} sinyali!"
            
            return f"{symbol}: Alert tetiklendi!"
            
        except Exception as e:
            return f"{alert['symbol']}: Alert!"


if __name__ == '__main__':
    # Test
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent
    manager = NotificationManager(base_dir)
    
    # Test alert
    test_alert = {
        'id': 'test_1',
        'symbol': 'AMD',
        'type': 'price_above',
        'condition': {'price': 220}
    }
    
    # Test signal
    test_signal = {
        'symbol': 'AMD',
        'decision': 'HOLD',
        'confidence': 85.0,
        'price': {'current': 225.50},
        'technical': {'rsi': 65.5}
    }
    
    # Test Telegram
    # manager.send_telegram(test_alert, test_signal)
    
    print("Notification Manager hazır!")
