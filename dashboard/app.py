"""
METHEFOR FİNANSAL ÖZGÜRLÜK v2.0 - Web Dashboard Backend
Flask + SocketIO + RESTful API + Alert System
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import os
import sys
from pathlib import Path
from datetime import datetime
import threading
import time

# Ana dizin
BASE_DIR = Path(__file__).parent.parent

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Global state
current_signals = []
latest_news = []
technical_data = {}

# Watchlist dosya yolu
WATCHLIST_FILE = BASE_DIR / 'config' / 'watchlist.json'

# Alert sistemi
alert_engine = None
notification_manager = None


def load_latest_data():
    """En son veriyi yükle"""
    global current_signals, latest_news, technical_data
    
    data_dir = BASE_DIR / 'data'
    
    try:
        signal_files = sorted(data_dir.glob('signals_*.json'), reverse=True)
        news_files = sorted(data_dir.glob('news_*.json'), reverse=True)
        tech_files = sorted(data_dir.glob('technical_*.json'), reverse=True)
        
        if signal_files:
            with open(signal_files[0], 'r', encoding='utf-8') as f:
                current_signals = json.load(f)
        
        if news_files:
            with open(news_files[0], 'r', encoding='utf-8') as f:
                latest_news = json.load(f)
        
        if tech_files:
            with open(tech_files[0], 'r', encoding='utf-8') as f:
                technical_data = json.load(f)
        
        print(f"✓ Data yüklendi: {len(current_signals)} sinyal, {len(latest_news)} haber")
        
    except Exception as e:
        print(f"Data yükleme hatası: {e}")


# Routes
@app.route('/')
def index():
    """Ana dashboard sayfası"""
    return render_template('index.html')


@app.route('/api/signals')
def get_signals():
    """Tüm sinyalleri döndür"""
    return jsonify({
        'success': True,
        'count': len(current_signals),
        'signals': current_signals,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/signals/<symbol>')
def get_symbol_signal(symbol):
    """Belirli bir sembolün sinyalini döndür"""
    symbol_upper = symbol.upper()
    signal = next((s for s in current_signals if s['symbol'] == symbol_upper), None)
    
    if signal:
        return jsonify({'success': True, 'signal': signal})
    else:
        return jsonify({'success': False, 'error': f'Signal not found for {symbol_upper}'}), 404


@app.route('/api/news')
def get_news():
    """Son haberleri döndür"""
    limit = request.args.get('limit', 20, type=int)
    
    return jsonify({
        'success': True,
        'count': len(latest_news),
        'news': latest_news[:limit],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/news/<symbol>')
def get_symbol_news(symbol):
    """Belirli bir sembolün haberlerini döndür"""
    symbol_upper = symbol.upper()
    
    symbol_news = [
        n for n in latest_news 
        if n.get('matched_symbol', '').upper() == symbol_upper
    ]
    
    return jsonify({
        'success': True,
        'symbol': symbol_upper,
        'count': len(symbol_news),
        'news': symbol_news
    })


@app.route('/api/technical/<symbol>')
def get_technical(symbol):
    """Belirli bir sembolün teknik analizini döndür"""
    symbol_upper = symbol.upper()
    tech = technical_data.get(symbol_upper)
    
    if tech:
        return jsonify({'success': True, 'technical': tech})
    else:
        return jsonify({'success': False, 'error': f'Technical data not found for {symbol_upper}'}), 404


@app.route('/api/summary')
def get_summary():
    """Dashboard özet istatistikleri"""
    
    strong_buy = sum(1 for s in current_signals if s['decision'] == 'STRONG BUY')
    buy = sum(1 for s in current_signals if s['decision'] == 'BUY')
    hold = sum(1 for s in current_signals if s['decision'] == 'HOLD')
    sell = sum(1 for s in current_signals if s['decision'] == 'SELL')
    strong_sell = sum(1 for s in current_signals if s['decision'] == 'STRONG SELL')
    
    top_signals = sorted(current_signals, key=lambda x: x['combined_score'], reverse=True)[:5]
    
    positive_news = sum(1 for n in latest_news if n.get('sentiment', {}).get('label') == 'positive')
    negative_news = sum(1 for n in latest_news if n.get('sentiment', {}).get('label') == 'negative')
    
    return jsonify({
        'success': True,
        'summary': {
            'total_signals': len(current_signals),
            'signal_distribution': {
                'strong_buy': strong_buy,
                'buy': buy,
                'hold': hold,
                'sell': sell,
                'strong_sell': strong_sell
            },
            'news_stats': {
                'total': len(latest_news),
                'positive': positive_news,
                'negative': negative_news,
                'neutral': len(latest_news) - positive_news - negative_news
            },
            'top_signals': top_signals
        },
        'timestamp': datetime.now().isoformat()
    })


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Client bağlandığında"""
    print('✓ Client connected - Methefor Finansal Özgürlük')
    emit('status', {'message': 'Connected to Methefor Financial Freedom'})
    
    emit('initial_data', {
        'signals': current_signals[:10],
        'news': latest_news[:20]
    })


@socketio.on('disconnect')
def handle_disconnect():
    """Client ayrıldığında"""
    print('✗ Client disconnected')


@socketio.on('request_update')
def handle_update_request():
    """Client güncelleme istediğinde"""
    load_latest_data()
    
    emit('data_update', {
        'signals': current_signals[:10],
        'news': latest_news[:20],
        'timestamp': datetime.now().isoformat()
    })


# ==========================================
# WATCHLIST API ENDPOINTS
# ==========================================

@app.route('/api/watchlist', methods=['GET'])
def get_watchlist():
    """Watchlist'i getir"""
    try:
        with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
            watchlist = json.load(f)
        
        all_symbols = []
        
        for category, symbols in watchlist.get('stocks', {}).items():
            for symbol in symbols:
                all_symbols.append({
                    'symbol': symbol,
                    'category': f'US_{category}',
                    'type': 'stock',
                    'market': 'US'
                })
        
        for symbol in watchlist.get('turkish_stocks', []):
            all_symbols.append({
                'symbol': symbol,
                'category': 'Turkish',
                'type': 'stock',
                'market': 'TR'
            })
        
        for symbol in watchlist.get('commodities', []):
            all_symbols.append({
                'symbol': symbol,
                'category': 'Commodities',
                'type': 'commodity',
                'market': 'GLOBAL'
            })
        
        for symbol in watchlist.get('crypto', []):
            all_symbols.append({
                'symbol': symbol,
                'category': 'Crypto',
                'type': 'crypto',
                'market': 'CRYPTO'
            })
        
        return jsonify({
            'success': True,
            'watchlist': all_symbols,
            'total': len(all_symbols),
            'categories': {
                'US': len([s for s in all_symbols if s['market'] == 'US']),
                'TR': len([s for s in all_symbols if s['market'] == 'TR']),
                'Commodities': len([s for s in all_symbols if s['type'] == 'commodity']),
                'Crypto': len([s for s in all_symbols if s['type'] == 'crypto'])
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Watchlist'e sembol ekle"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        category = data.get('category', 'custom')
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Sembol boş olamaz'}), 400
        
        with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
            watchlist = json.load(f)
        
        all_current = []
        for cat_symbols in watchlist.get('stocks', {}).values():
            all_current.extend(cat_symbols)
        all_current.extend(watchlist.get('turkish_stocks', []))
        all_current.extend(watchlist.get('commodities', []))
        all_current.extend(watchlist.get('crypto', []))
        
        if symbol in all_current:
            return jsonify({'success': False, 'error': f'{symbol} zaten watchlist\'te'}), 400
        
        if category == 'crypto' or symbol.endswith('-USD'):
            if 'crypto' not in watchlist:
                watchlist['crypto'] = []
            watchlist['crypto'].append(symbol)
            added_category = 'Crypto'
        
        elif category == 'turkish' or symbol.endswith('.IS'):
            if 'turkish_stocks' not in watchlist:
                watchlist['turkish_stocks'] = []
            watchlist['turkish_stocks'].append(symbol)
            added_category = 'Turkish'
        
        elif category in ['SLV', 'GLD', 'GC=F', 'SI=F']:
            if 'commodities' not in watchlist:
                watchlist['commodities'] = []
            watchlist['commodities'].append(symbol)
            added_category = 'Commodities'
        
        else:
            if 'stocks' not in watchlist:
                watchlist['stocks'] = {}
            if 'custom' not in watchlist['stocks']:
                watchlist['stocks']['custom'] = []
            watchlist['stocks']['custom'].append(symbol)
            added_category = 'US_custom'
        
        with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(watchlist, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'{symbol} başarıyla eklendi',
            'symbol': symbol,
            'category': added_category
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    """Watchlist'ten sembol sil"""
    try:
        data = request.get_json()
        symbol = data.get('symbol', '').upper().strip()
        
        if not symbol:
            return jsonify({'success': False, 'error': 'Sembol boş olamaz'}), 400
        
        with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
            watchlist = json.load(f)
        
        removed = False
        removed_from = ''
        
        if 'stocks' in watchlist:
            for category, symbols in watchlist['stocks'].items():
                if symbol in symbols:
                    watchlist['stocks'][category].remove(symbol)
                    removed = True
                    removed_from = f'US_{category}'
                    break
        
        if not removed and 'turkish_stocks' in watchlist and symbol in watchlist['turkish_stocks']:
            watchlist['turkish_stocks'].remove(symbol)
            removed = True
            removed_from = 'Turkish'
        
        if not removed and 'commodities' in watchlist and symbol in watchlist['commodities']:
            watchlist['commodities'].remove(symbol)
            removed = True
            removed_from = 'Commodities'
        
        if not removed and 'crypto' in watchlist and symbol in watchlist['crypto']:
            watchlist['crypto'].remove(symbol)
            removed = True
            removed_from = 'Crypto'
        
        if not removed:
            return jsonify({'success': False, 'error': f'{symbol} watchlist\'te bulunamadı'}), 404
        
        with open(WATCHLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump(watchlist, f, indent=2, ensure_ascii=False)
        
        return jsonify({
            'success': True,
            'message': f'{symbol} başarıyla silindi',
            'symbol': symbol,
            'removed_from': removed_from
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# ALERT SİSTEMİ - API ENDPOINTS
# ==========================================

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    """Tüm alert'leri getir"""
    try:
        if not alert_engine:
            return jsonify({'success': False, 'error': 'Alert engine yüklenmedi'}), 500
        
        alerts = alert_engine.alerts
        
        return jsonify({
            'success': True,
            'alerts': alerts,
            'count': len(alerts)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/add', methods=['POST'])
def add_alert():
    """Yeni alert ekle"""
    try:
        if not alert_engine:
            return jsonify({'success': False, 'error': 'Alert engine yüklenmedi'}), 500
        
        data = request.get_json()
        
        # Zorunlu alanları kontrol et
        if not data.get('symbol'):
            return jsonify({'success': False, 'error': 'Sembol gerekli'}), 400
        
        if not data.get('type'):
            return jsonify({'success': False, 'error': 'Alert tipi gerekli'}), 400
        
        # Alert ekle
        alert = alert_engine.add_alert(data)
        
        if alert:
            return jsonify({
                'success': True,
                'alert': alert,
                'message': f'{alert["symbol"]} için alert oluşturuldu'
            })
        else:
            return jsonify({'success': False, 'error': 'Alert eklenemedi'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/remove', methods=['POST'])
def remove_alert():
    """Alert sil"""
    try:
        if not alert_engine:
            return jsonify({'success': False, 'error': 'Alert engine yüklenmedi'}), 500
        
        data = request.get_json()
        alert_id = data.get('alert_id')
        
        if not alert_id:
            return jsonify({'success': False, 'error': 'Alert ID gerekli'}), 400
        
        success = alert_engine.remove_alert(alert_id)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Alert silindi'
            })
        else:
            return jsonify({'success': False, 'error': 'Alert silinemedi'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/toggle', methods=['POST'])
def toggle_alert():
    """Alert'i aktif/pasif yap"""
    try:
        if not alert_engine:
            return jsonify({'success': False, 'error': 'Alert engine yüklenmedi'}), 500
        
        data = request.get_json()
        alert_id = data.get('alert_id')
        enabled = data.get('enabled', True)
        
        if not alert_id:
            return jsonify({'success': False, 'error': 'Alert ID gerekli'}), 400
        
        success = alert_engine.toggle_alert(alert_id, enabled)
        
        if success:
            status = 'aktif' if enabled else 'pasif'
            return jsonify({
                'success': True,
                'message': f'Alert {status} edildi'
            })
        else:
            return jsonify({'success': False, 'error': 'Alert güncellenemedi'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/history', methods=['GET'])
def get_alert_history():
    """Tetiklenmiş alert geçmişi"""
    try:
        if not alert_engine:
            return jsonify({'success': False, 'error': 'Alert engine yüklenmedi'}), 500
        
        limit = request.args.get('limit', 50, type=int)
        history = alert_engine.get_alert_history(limit)
        
        return jsonify({
            'success': True,
            'history': history,
            'count': len(history)
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/alerts/test', methods=['POST'])
def test_alert():
    """Test alert gönder"""
    try:
        if not alert_engine or not notification_manager:
            return jsonify({'success': False, 'error': 'Alert sistemi yüklenmedi'}), 500
        
        data = request.get_json()
        alert_id = data.get('alert_id')
        
        if not alert_id:
            return jsonify({'success': False, 'error': 'Alert ID gerekli'}), 400
        
        # Alert'i bul
        alert = None
        for a in alert_engine.alerts:
            if a['id'] == alert_id:
                alert = a
                break
        
        if not alert:
            return jsonify({'success': False, 'error': 'Alert bulunamadı'}), 404
        
        # Test sinyali oluştur
        test_signal = {
            'symbol': alert['symbol'],
            'decision': 'HOLD',
            'confidence': 85.0,
            'combined_score': 75,
            'price': {'current': 200.0},
            'technical': {'rsi': 50.0}
        }
        
        # Test bildirimi gönder
        success = alert_engine.trigger_alert(alert, [test_signal], notification_manager)
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Test alert gönderildi'
            })
        else:
            return jsonify({'success': False, 'error': 'Test alert gönderilemedi'}), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def background_update_task():
    """Arka planda veri güncelleme (her 30 saniye)"""
    while True:
        time.sleep(30)
        load_latest_data()
        
        socketio.emit('data_update', {
            'signals': current_signals[:10],
            'news': latest_news[:20],
            'timestamp': datetime.now().isoformat()
        }, namespace='/')
        
        # Alert kontrolü
        if alert_engine and notification_manager and current_signals:
            try:
                triggered = alert_engine.check_alerts(current_signals, notification_manager)
                if triggered:
                    print(f"🚨 {len(triggered)} alert tetiklendi")
            except Exception as e:
                print(f"Alert kontrol hatası: {e}")


def main():
    """Dashboard'u başlat"""
    global alert_engine, notification_manager
    
    print("\n" + "="*60)
    print("💰 METHEFOR FİNANSAL ÖZGÜRLÜK - WEB DASHBOARD v2.0")
    print("="*60)
    
    print("\n📊 İlk veri yükleniyor...")
    load_latest_data()
    
    # Alert sistemi başlat
    print("\n🔔 Alert sistemi başlatılıyor...")
    try:
        # src klasörünü Python path'ine ekle
        src_path = str(BASE_DIR / 'src')
        if src_path not in sys.path:
            sys.path.insert(0, src_path)
        
        from alert_engine import AlertEngine
        from notification_manager import NotificationManager
        
        alert_engine = AlertEngine(BASE_DIR)
        notification_manager = NotificationManager(BASE_DIR, socketio)
        
        print(f"✓ {len(alert_engine.alerts)} alert yüklendi")
        print("✓ Notification manager hazır")
    except Exception as e:
        print(f"⚠️ Alert sistemi hatası: {e}")
        import traceback
        traceback.print_exc()
        alert_engine = None
        notification_manager = None
    
    # Background task başlat
    update_thread = threading.Thread(target=background_update_task, daemon=True)
    update_thread.start()
    
    print("\n✓ Dashboard hazır!")
    print("\n📱 Tarayıcıda aç:")
    print("   http://localhost:5000")
    print("\n⏹️ Durdurmak için: Ctrl+C")
    print("="*60 + "\n")
    
    socketio.run(app, host='0.0.0.0', port=5000, debug=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    main()