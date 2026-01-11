"""
METHEFOR FİNANSAL ÖZGÜRLÜK v2.1 - Web Dashboard Backend
Flask + SocketIO + RESTful API + SQLite
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
sys.path.insert(0, str(BASE_DIR))

# Database Imports
from src.database import init_db, get_session, NewsItem, TechnicalResult, Signal, PortfolioItem
from src.ai.chatbot import AIChatbot

app = Flask(__name__, 
            template_folder='templates',
            static_folder='static')
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Database Engine
db_engine = init_db(str(BASE_DIR / 'methefor.db'))

# Watchlist dosya yolu
WATCHLIST_FILE = BASE_DIR / 'config' / 'watchlist.json'
SETTINGS_FILE = BASE_DIR / 'config' / 'settings.json'

class AppData:
    """Uygulama verilerini ve ayarlarını yöneten sınıf"""
    def __init__(self):
        self.current_signals = []
        self.latest_news = []
        self.technical_data = {}
        self.portfolio_summary = {}
        self.chatbot = AIChatbot()
        self.settings = self.load_settings()

    def load_settings(self):
        if SETTINGS_FILE.exists():
            with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {"ui": {"theme": "dark"}, "analysis": {"rsi_overbought": 70}}

    def save_settings(self, new_settings):
        self.settings.update(new_settings)
        with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.settings, f, indent=2, ensure_ascii=False)

data = AppData()


def load_latest_data():
    """En son veriyi veritabanından yükle"""
    session = get_session(db_engine)
    try:
        # 1. Signals
        db_signals = session.query(Signal).order_by(Signal.timestamp.desc()).limit(100).all()
        
        temp_signals = {}
        for s in db_signals:
            if s.symbol not in temp_signals:
                reasons = json.loads(s.reasons) if s.reasons else []
                formatted_sig = {
                    'symbol': s.symbol,
                    'decision': s.decision,
                    'combined_score': s.combined_score,
                    'confidence': s.confidence,
                    'sentiment': {
                        'score': s.news_sentiment_score,
                        'label': 'positive' if s.news_sentiment_score > 0.1 else 'negative' if s.news_sentiment_score < -0.1 else 'neutral',
                        'news_count': 0
                    },
                    'technical': {
                        'score': s.technical_score,
                        'decision': 'N/A',
                        'trend': 'N/A'
                    },
                    'price': {'current': 0},
                    'reasons': reasons,
                    'ai_explanation': s.ai_explanation,
                    'timestamp': s.timestamp.isoformat()
                }
                temp_signals[s.symbol] = formatted_sig
        
        data.current_signals = list(temp_signals.values())
        data.current_signals.sort(key=lambda x: x['combined_score'], reverse=True)

        # 2. News
        db_news = session.query(NewsItem).order_by(NewsItem.published_date.desc()).limit(50).all()
        data.latest_news = []
        for n in db_news:
            data.latest_news.append({
                'id': n.id,
                'source': n.source,
                'title': n.title,
                'summary': n.summary,
                'link': n.link,
                'published': n.published_date.isoformat() if n.published_date else "",
                'category': n.category,
                'sentiment': {
                    'score': n.sentiment_score,
                    'label': n.sentiment_label or ('positive' if n.sentiment_score > 0 else 'negative' if n.sentiment_score < 0 else 'neutral')
                },
                'matched_symbol': json.loads(n.related_symbols)[0] if n.related_symbols and len(json.loads(n.related_symbols)) > 0 else None
            })

        # 3. Technical
        db_tech = session.query(TechnicalResult).order_by(TechnicalResult.timestamp.desc()).limit(100).all()
        
        data.technical_data = {}
        for t in db_tech:
            if t.symbol not in data.technical_data:
                details = json.loads(t.details) if t.details else {}
                data.technical_data[t.symbol] = details
                
                matching_signal = next((s for s in data.current_signals if s['symbol'] == t.symbol), None)
                if matching_signal:
                    matching_signal['technical']['rsi'] = t.rsi
                    matching_signal['technical']['trend'] = t.trend
                    matching_signal['price'] = {'current': t.price}
                    if 'technical_signals' in details:
                        matching_signal['technical']['decision'] = details['technical_signals'].get('decision', 'N/A')

        # 4. Portfolio
        db_portfolio = session.query(PortfolioItem).all()
        data.portfolio_summary = {'total_equity': 0, 'cash': 0, 'holdings': []}
        
        equity = 0
        for p in db_portfolio:
            if p.symbol == 'USD':
                data.portfolio_summary['cash'] = p.quantity
                equity += p.quantity
            else:
                value = p.quantity * p.current_price
                equity += value
                data.portfolio_summary['holdings'].append({
                    'symbol': p.symbol,
                    'quantity': p.quantity,
                    'price': p.current_price,
                    'value': value,
                    'avg_price': p.average_price,
                    'pnl': (p.current_price - p.average_price) / p.average_price * 100 if p.average_price else 0
                })
        data.portfolio_summary['total_equity'] = equity
        print(f"✓ DB Data yüklendi: {len(data.current_signals)} sinyal, Portfolio: ${equity:.2f}")
    finally:
        session.close()


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
        'count': len(data.current_signals),
        'signals': data.current_signals,
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/signals/<symbol>')
def get_symbol_signal(symbol):
    """Belirli bir sembolün sinyalini döndür"""
    symbol_upper = symbol.upper()
    signal = next((s for s in data.current_signals if s['symbol'] == symbol_upper), None)
    
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
        'count': len(data.latest_news),
        'news': data.latest_news[:limit],
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/news/<symbol>')
def get_symbol_news(symbol):
    """Belirli bir sembolün haberlerini döndür"""
    symbol_upper = symbol.upper()
    
    symbol_news = [
        n for n in data.latest_news 
        if n.get('matched_symbol') == symbol_upper
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
    tech = data.technical_data.get(symbol_upper)
    
    if tech:
        return jsonify({'success': True, 'technical': tech})
    else:
        return jsonify({'success': False, 'error': f'Technical data not found for {symbol_upper}'}), 404


@app.route('/api/summary')
def get_summary():
    """Dashboard özet istatistikleri"""
    
    strong_buy = sum(1 for s in data.current_signals if s['decision'] == 'STRONG BUY')
    buy = sum(1 for s in data.current_signals if s['decision'] == 'BUY')
    hold = sum(1 for s in data.current_signals if s['decision'] == 'HOLD')
    sell = sum(1 for s in data.current_signals if s['decision'] == 'SELL')
    strong_sell = sum(1 for s in data.current_signals if s['decision'] == 'STRONG SELL')
    
    top_signals = sorted(data.current_signals, key=lambda x: x['combined_score'], reverse=True)[:5]
    
    positive_news = sum(1 for n in data.latest_news if n.get('sentiment', {}).get('label') == 'positive')
    negative_news = sum(1 for n in data.latest_news if n.get('sentiment', {}).get('label') == 'negative')
    
    return jsonify({
        'success': True,
        'summary': {
            'total_signals': len(data.current_signals),
            'signal_distribution': {
                'strong_buy': strong_buy,
                'buy': buy,
                'hold': hold,
                'sell': sell,
                'strong_sell': strong_sell
            },
            'news_stats': {
                'total': len(data.latest_news),
                'positive': positive_news,
                'negative': negative_news,
                'neutral': len(data.latest_news) - positive_news - negative_news
            },
            'top_signals': top_signals
        },
        'timestamp': datetime.now().isoformat()
    })


@app.route('/api/portfolio')
def get_portfolio():
    """Portföy durumunu döndür"""
    return jsonify({
        'success': True,
        'portfolio': data.portfolio_summary,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/settings', methods=['GET', 'POST'])
def handle_settings():
    """Ayarları getir veya güncelle"""
    if request.method == 'GET':
        return jsonify({'success': True, 'settings': data.settings})
    else:
        new_settings = request.json
        data.save_settings(new_settings)
        return jsonify({'success': True, 'message': 'Ayarlar kaydedildi'})


@app.route('/api/chat', methods=['POST'])
def chat():
    """AI Chatbot ile konuş"""
    data_req = request.json
    user_message = data_req.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'Mesaj boş olamaz'}), 400
        
    response = data.chatbot.send_message(user_message)
    
    return jsonify({
        'success': True,
        'response': response,
        'timestamp': datetime.now().isoformat()
    })


# WebSocket events
@socketio.on('connect')
def handle_connect():
    """Client bağlandığında"""
    print('✓ Client connected - Methefor Finansal Özgürlük')
    emit('status', {'message': 'Connected to Methefor Financial Freedom'})
    
    emit('initial_data', {
        'signals': data.current_signals[:10],
        'news': data.latest_news[:20],
        'portfolio': data.portfolio_summary,
        'settings': data.settings
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
        'signals': data.current_signals[:10],
        'news': data.latest_news[:20],
        'timestamp': datetime.now().isoformat()
    })


# ==========================================
# WATCHLIST API ENDPOINTS (Existing Logic)
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
        
        # Read from file
        if os.path.exists(WATCHLIST_FILE):
             with open(WATCHLIST_FILE, 'r', encoding='utf-8') as f:
                watchlist = json.load(f)
        else:
            watchlist = {'stocks': {'custom': []}}

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


def background_update_task():
    """Arka planda veri güncelleme (her 30 saniye)"""
    while True:
        time.sleep(30)
        load_latest_data()
        
        socketio.emit('data_update', {
            'signals': data.current_signals[:10],
            'news': data.latest_news[:20],
            'portfolio': data.portfolio_summary,
            'timestamp': datetime.now().isoformat()
        }, namespace='/')


def main():
    """Dashboard'u başlat"""
    
    print("\n" + "="*60)
    print("💰 METHEFOR FİNANSAL ÖZGÜRLÜK - WEB DASHBOARD (DB CONNECTED)")
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
