"""
Alert Engine - Methefor Finansal Özgürlük
Alert koşullarını kontrol eder ve bildirimleri tetikler
"""

import json
import os
from pathlib import Path
from datetime import datetime
import time

class AlertEngine:
    def __init__(self, base_dir):
        self.base_dir = Path(base_dir)
        self.alerts_file = self.base_dir / 'config' / 'alerts.json'
        self.alerts = self.load_alerts()
        
    def load_alerts(self):
        """Alert'leri yükle"""
        try:
            if self.alerts_file.exists():
                with open(self.alerts_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('alerts', [])
            else:
                # İlk kez oluştur
                self.save_alerts([])
                return []
        except Exception as e:
            print(f"Alert yükleme hatası: {e}")
            return []
    
    def save_alerts(self, alerts=None):
        """Alert'leri kaydet"""
        if alerts is None:
            alerts = self.alerts
            
        try:
            # Config klasörünü oluştur
            self.alerts_file.parent.mkdir(parents=True, exist_ok=True)
            
            with open(self.alerts_file, 'w', encoding='utf-8') as f:
                json.dump({'alerts': alerts}, f, indent=2, ensure_ascii=False)
            
            print(f"✓ {len(alerts)} alert kaydedildi")
        except Exception as e:
            print(f"Alert kaydetme hatası: {e}")
    
    def check_alerts(self, signals, notification_manager):
        """Tüm alert'leri kontrol et"""
        triggered_alerts = []
        
        for alert in self.alerts:
            if not alert.get('enabled', True):
                continue
            
            # Alert koşulunu değerlendir
            if self.evaluate_condition(alert, signals):
                # Bildirim gönder
                triggered = self.trigger_alert(alert, signals, notification_manager)
                if triggered:
                    triggered_alerts.append(alert)
        
        return triggered_alerts
    
    def evaluate_condition(self, alert, signals):
        """Alert koşulunu değerlendir"""
        try:
            # İlgili sinyali bul
            signal = self.find_signal(alert['symbol'], signals)
            if not signal:
                return False
            
            alert_type = alert['type']
            condition = alert.get('condition', {})
            
            # Alert tipine göre kontrol et
            if alert_type == 'price_above':
                current_price = signal.get('price', {}).get('current', 0)
                target_price = condition.get('price', 0)
                return current_price > target_price
            
            elif alert_type == 'price_below':
                current_price = signal.get('price', {}).get('current', 0)
                target_price = condition.get('price', 0)
                return current_price < target_price
            
            elif alert_type == 'price_change':
                change = signal.get('price', {}).get('change_1d', 0)
                target_change = condition.get('change_pct', 0)
                return abs(change) > target_change
            
            elif alert_type == 'rsi_above':
                rsi = signal.get('technical', {}).get('rsi', 50)
                target_rsi = condition.get('rsi', 70)
                return rsi > target_rsi
            
            elif alert_type == 'rsi_below':
                rsi = signal.get('technical', {}).get('rsi', 50)
                target_rsi = condition.get('rsi', 30)
                return rsi < target_rsi
            
            elif alert_type == 'new_signal':
                decision = signal.get('decision', 'HOLD')
                target_decision = condition.get('decision', 'STRONG BUY')
                return decision == target_decision
            
            elif alert_type == 'volume_spike':
                volume = signal.get('price', {}).get('volume', 0)
                avg_volume = signal.get('price', {}).get('avg_volume', 0)
                multiplier = condition.get('multiplier', 2)
                if avg_volume > 0:
                    return volume > (avg_volume * multiplier)
                return False
            
            return False
            
        except Exception as e:
            print(f"Alert değerlendirme hatası ({alert.get('symbol')}): {e}")
            return False
    
    def find_signal(self, symbol, signals):
        """Sembolün sinyalini bul"""
        for signal in signals:
            if signal.get('symbol', '').upper() == symbol.upper():
                return signal
        return None
    
    def trigger_alert(self, alert, signals, notification_manager):
        """Alert'i tetikle ve bildirim gönder"""
        try:
            # Rate limiting - aynı alert 1 saatte 1 kez
            last_triggered = alert.get('last_triggered')
            if last_triggered:
                last_time = datetime.fromisoformat(last_triggered)
                now = datetime.now()
                diff = (now - last_time).total_seconds()
                
                # 1 saat = 3600 saniye
                if diff < 3600:
                    print(f"⏳ Alert rate limited: {alert['symbol']} ({diff:.0f}s önce tetiklendi)")
                    return False
            
            # Sinyal bilgilerini al
            signal = self.find_signal(alert['symbol'], signals)
            
            # Bildirim gönder
            actions = alert.get('actions', [])
            success = False
            
            for action in actions:
                try:
                    if action == 'telegram':
                        notification_manager.send_telegram(alert, signal)
                        success = True
                    elif action == 'email':
                        notification_manager.send_email(alert, signal)
                        success = True
                    elif action == 'browser':
                        notification_manager.send_browser_notification(alert, signal)
                        success = True
                except Exception as e:
                    print(f"Bildirim gönderme hatası ({action}): {e}")
            
            if success:
                # Alert kaydını güncelle
                alert['last_triggered'] = datetime.now().isoformat()
                alert['trigger_count'] = alert.get('trigger_count', 0) + 1
                self.save_alerts()
                
                print(f"🚨 Alert tetiklendi: {alert['symbol']} ({alert['type']})")
                return True
            
            return False
            
        except Exception as e:
            print(f"Alert tetikleme hatası: {e}")
            return False
    
    def add_alert(self, alert_data):
        """Yeni alert ekle"""
        try:
            # ID oluştur
            alert_id = f"alert_{int(time.time() * 1000)}"
            
            alert = {
                'id': alert_id,
                'symbol': alert_data['symbol'].upper(),
                'type': alert_data['type'],
                'condition': alert_data.get('condition', {}),
                'actions': alert_data.get('actions', ['telegram']),
                'enabled': True,
                'created_at': datetime.now().isoformat(),
                'last_triggered': None,
                'trigger_count': 0
            }
            
            self.alerts.append(alert)
            self.save_alerts()
            
            print(f"✓ Yeni alert eklendi: {alert['symbol']}")
            return alert
            
        except Exception as e:
            print(f"Alert ekleme hatası: {e}")
            return None
    
    def remove_alert(self, alert_id):
        """Alert sil"""
        try:
            self.alerts = [a for a in self.alerts if a['id'] != alert_id]
            self.save_alerts()
            
            print(f"✓ Alert silindi: {alert_id}")
            return True
            
        except Exception as e:
            print(f"Alert silme hatası: {e}")
            return False
    
    def toggle_alert(self, alert_id, enabled):
        """Alert'i aktif/pasif yap"""
        try:
            for alert in self.alerts:
                if alert['id'] == alert_id:
                    alert['enabled'] = enabled
                    self.save_alerts()
                    
                    status = "aktif" if enabled else "pasif"
                    print(f"✓ Alert {status}: {alert['symbol']}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"Alert toggle hatası: {e}")
            return False
    
    def get_alert_history(self, limit=50):
        """Tetiklenmiş alert geçmişi"""
        try:
            # Trigger count > 0 olanları al
            triggered = [a for a in self.alerts if a.get('trigger_count', 0) > 0]
            
            # Son tetiklenme zamanına göre sırala
            triggered.sort(key=lambda a: a.get('last_triggered', ''), reverse=True)
            
            return triggered[:limit]
            
        except Exception as e:
            print(f"Alert history hatası: {e}")
            return []


if __name__ == '__main__':
    # Test
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent
    engine = AlertEngine(base_dir)
    
    # Test alert ekle
    test_alert = {
        'symbol': 'AMD',
        'type': 'price_above',
        'condition': {'price': 220},
        'actions': ['telegram']
    }
    
    result = engine.add_alert(test_alert)
    print(f"Test alert: {result}")
