
import os
import logging
import json
import google.generativeai as genai
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AIAnalyst:
    """
    Yapay Zeka Finansal Analist
    Google Gemini API kullanarak sinyalleri yorumlar.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        self.enabled = False
        
        if self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.5-flash')
                self.enabled = True
                logger.info("[OK] AI Analyst (Gemini) aktifleştirildi.")
            except Exception as e:
                logger.error(f"AI Connection Error: {e}")
        else:
            logger.warning("AI Analyst: API Key bulunamadı (GEMINI_API_KEY). AI özellikleri devre dışı.")

    def explain_signal(self, symbol: str, signal_data: Dict, news_context: list = []) -> str:
        """
        Sinyal için Çoklu Ajan Sistemi üzerinden kapsamlı bir açıklama üretir.
        """
        if not self.enabled:
            return self._fallback_explanation(symbol, signal_data)
            
        try:
            from src.ai.multi_agent import multi_agent_system
            import asyncio

            # Async metodu senkronize olarak çalıştır (dashboard uyumluluğu için)
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # Eğer event loop zaten çalışıyorsa (dashboard gibi), yeni bir görev oluşturamayız
                # Bu yüzden basitleştirilmiş bir sentez yapıyoruz
                return self._sync_explain(symbol, signal_data, news_context)
            else:
                analysis = loop.run_until_complete(
                    multi_agent_system.get_comprehensive_analysis(symbol, signal_data, news_context)
                )
                return analysis
            
        except Exception as e:
            logger.error(f"AI Generation Error for {symbol}: {e}")
            return self._sync_explain(symbol, signal_data, news_context)

    def _sync_explain(self, symbol: str, signal_data: Dict, news_context: list = []) -> str:
        """Senkronize basitleştirilmiş analiz"""
        try:
            tech_signals = ", ".join(signal_data.get('reasons', []))
            decision = signal_data.get('decision', 'HOLD')
            news_text = "\n".join([f"- {n.get('title')}" for n in news_context[:2]]) if news_context else ""
            
            prompt = f"Baş Analist olarak {symbol} için {decision} kararını özetle. Teknik: {tech_signals}. Haberler: {news_text}. 2 cümle."
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except:
            return self._fallback_explanation(symbol, signal_data)

    def _fallback_explanation(self, symbol: str, signal_data: Dict) -> str:
        """API çalışmazsa standart şablon"""
        decision = signal_data.get('decision', 'HOLD')
        reasons = signal_data.get('reasons', [])
        reasons_str = ", ".join(reasons) if reasons else "Yetersiz veri"
        return f"{symbol} için {decision} sinyali üretildi. Öne çıkan göstergeler: {reasons_str}."
