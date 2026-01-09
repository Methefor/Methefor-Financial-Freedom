
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
                self.model = genai.GenerativeModel('gemini-pro')
                self.enabled = True
                logger.info("[OK] AI Analyst (Gemini) aktifleştirildi.")
            except Exception as e:
                logger.error(f"AI Connection Error: {e}")
        else:
            logger.warning("AI Analyst: API Key bulunamadı (GEMINI_API_KEY). AI özellikleri devre dışı.")

    def explain_signal(self, symbol: str, signal_data: Dict, news_context: list = []) -> str:
        """
        Sinyal için kısa, profesyonel bir açıklama üretir.
        """
        if not self.enabled:
            return self._fallback_explanation(symbol, signal_data)
            
        try:
            # Context oluştur
            tech_signals = ", ".join(signal_data.get('reasons', []))
            score = signal_data.get('combined_score', 0)
            decision = signal_data.get('decision', 'HOLD')
            
            # Haber özetlerini birleştir (max 3 haber)
            news_text = ""
            if news_context:
                news_text = "Son Haberler:\n" + "\n".join([f"- {n.get('title')}" for n in news_context[:3]])
            
            prompt = f"""
            Sen kıdemli bir finansal analistsin. Aşağıdaki verileri kullanarak {symbol} için neden {decision} kararı verildiğini 2 cümle ile açıkla.
            
            Teknik Veriler:
            - Karar: {decision} (Skor: {score}/100)
            - Göstergeler: {tech_signals}
            
            {news_text}
            
            Yorumun profesyonel, yatırım tavsiyesi vermeden (YTD) sadece teknik ve temel analizi özetleyen Türkçe bir açıklama olsun.
            """
            
            response = self.model.generate_content(prompt)
            return response.text.strip()
            
        except Exception as e:
            logger.error(f"AI Generation Error for {symbol}: {e}")
            return self._fallback_explanation(symbol, signal_data)

    def _fallback_explanation(self, symbol: str, signal_data: Dict) -> str:
        """API çalışmazsa standart şablon"""
        decision = signal_data.get('decision', 'HOLD')
        reasons = signal_data.get('reasons', [])
        reasons_str = ", ".join(reasons) if reasons else "Yetersiz veri"
        return f"{symbol} için {decision} sinyali üretildi. Öne çıkan göstergeler: {reasons_str}."
