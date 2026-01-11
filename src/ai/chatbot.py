import google.generativeai as genai
import os
import json
import logging
from typing import List, Dict
from pathlib import Path

logger = logging.getLogger(__name__)

class AIChatbot:
    def __init__(self):
        self.api_key = self._load_api_key()
        self.model = None
        self.chat_session = None
        self.history = []
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.start_new_session()
                logger.info("AIChatbot initialized successfully")
            except Exception as e:
                logger.error(f"AIChatbot initialization failed: {e}")
        else:
            logger.warning("AIChatbot disabled: API Key not found")

    def _load_api_key(self):
        """Load API key from config or env"""
        try:
            # First try environment variable
            key = os.getenv('GEMINI_API_KEY')
            if key: return key
            
            # Then try config file
            # Robust way to find absolute root of project
            current_file = os.path.abspath(__file__) # .../src/ai/chatbot.py
            src_dir = os.path.dirname(os.path.dirname(current_file)) # .../src
            project_root = os.path.dirname(src_dir) # .../root
            config_path = os.path.join(project_root, 'config', 'api_keys.json')
            
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    data = json.load(f)
                    return data.get('gemini_api_key')
        except Exception as e:
            logger.error(f"Error loading API key: {e}")
        return None

    def start_new_session(self):
        """Start a fresh chat session"""
        if self.model:
            self.chat_session = self.model.start_chat(history=[])
            initial_prompt = "Sen Methefor Finansal Özgürlük asistanısın. Kullanıcıya borsa, finans ve sistemin durumu hakkında yardımcı ol. Kısa ve öz cevaplar ver."
            self.chat_session.send_message(initial_prompt)
            self.history = []

    def _get_system_context(self) -> str:
        """Veritabanından güncel durumu çek ve metin olarak döndür"""
        try:
            from src.database import init_db, get_session, PortfolioItem, Signal
            project_root = Path(__file__).parent.parent.parent
            engine = init_db(str(project_root / "methefor.db"))
            session = get_session(engine)
            
            # Portföy özeti
            portfolio = session.query(PortfolioItem).all()
            p_text = "Portföy: " + ", ".join([f"{p.symbol} ({p.quantity} adet)" for p in portfolio if p.quantity > 0])
            
            # Son sinyaller
            signals = session.query(Signal).order_by(Signal.timestamp.desc()).limit(5).all()
            s_text = "Son Sinyaller: " + ", ".join([f"{s.symbol} ({s.decision})" for s in signals])
            
            session.close()
            return f"\n[SİSTEM DURUMU]\n{p_text}\n{s_text}\n"
        except Exception as e:
            logger.error(f"Context error: {e}")
            return ""

    def send_message(self, message: str) -> str:
        """Send message to AI with context and get response"""
        if not self.model or not self.chat_session:
            return "⚠️ AI Asistanı aktif değil (API Anahtarı eksik)."
        
        try:
            # Her mesajda güncel bağlamı ekle
            context = self._get_system_context()
            full_message = f"{context}\nKullanıcı Sorusu: {message}"
            
            response = self.chat_session.send_message(full_message)
            return response.text
        except Exception as e:
            error_msg = str(e)
            logger.error(f"Chat error: {error_msg}")
            if "quota" in error_msg.lower():
                return "❌ API kota sınırına ulaşıldı. Lütfen bir süre bekleyin."
            if "finish_reason" in error_msg.lower():
                return "❌ AI yanıtı güvenlik filtresine takıldı. Lütfen farklı bir soru sorun."
            return f"❌ AI hatası: {error_msg[:100]}..."

    def get_history(self) -> List[Dict]:
        """Return chat history (simplified for frontend)"""
        # Gemini history object is complex, we might maintain our own simple list or parse theirs
        # For simplicity, let's rely on what we store or just return empty if not needed
        # The frontend usually appends messages locally.
        return []
