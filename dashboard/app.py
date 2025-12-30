"""
METHEFOR FİNANSAL ÖZGÜRLÜK v1.0 - Web Dashboard Backend
Flask + SocketIO + RESTful API
"""

from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json
import os
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


def main():
    """Dashboard'u başlat"""
    
    print("\n" + "="*60)
    print("💰 METHEFOR FİNANSAL ÖZGÜRLÜK - WEB DASHBOARD")
    print("="*60)
    
    print("\n📊 İlk veri yükleniyor...")
    load_latest_data()
    
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
