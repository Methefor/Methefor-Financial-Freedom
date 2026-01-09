import google.generativeai as genai
import os
import json
import logging
from typing import List, Dict

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
                self.model = genai.GenerativeModel('gemini-1.5-flash')
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
            config_path = os.path.join(os.getcwd(), 'config', 'api_keys.json')
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
            # System prompt can be injected as the first message or configured if supported
            # For Gemini Pro via API, we often just start chatting.
            # But we can prime it:
            initial_prompt = "Sen Methefor Finansal Özgürlük asistanısın. Kullanıcıya borsa, finans ve sistemin durumu hakkında yardımcı ol. Kısa ve öz cevaplar ver."
            self.chat_session.send_message(initial_prompt)
            self.history = []

    def send_message(self, message: str) -> str:
        """Send message to AI and get response"""
        if not self.model or not self.chat_session:
            return "⚠️ AI Asistanı aktif değil (API Anahtarı eksik)."
        
        try:
            response = self.chat_session.send_message(message)
            return response.text
        except Exception as e:
            logger.error(f"Chat error: {e}")
            return "❌ Bir hata oluştu. Lütfen tekrar deneyin."

    def get_history(self) -> List[Dict]:
        """Return chat history (simplified for frontend)"""
        # Gemini history object is complex, we might maintain our own simple list or parse theirs
        # For simplicity, let's rely on what we store or just return empty if not needed
        # The frontend usually appends messages locally.
        return []
