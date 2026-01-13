import google.generativeai as genai
import logging
import os
from typing import Dict, List, Optional

logger = logging.getLogger(__name__)

class MultiAgentSystem:
    """
    Methefor Çoklu Ajan Denetim Sistemi.
    Farklı uzmanlık alanlarına sahip ajanları yönetir ve analizleri sentezler.
    """
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv('GEMINI_API_KEY')
        if not self.api_key:
            logger.warning("MultiAgentSystem: API Key bulunamadı.")
            self.enabled = False
            return
            
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.enabled = True

    async def get_comprehensive_analysis(self, symbol: str, tech_data: Dict, news_context: List[Dict]) -> str:
        """Tüm ajanları çalıştır ve sentezlenmiş rapor al"""
        if not self.enabled:
            return "Analiz yapılamadı: AI devre dışı."

        # 1. Uzman Görüşlerini Topla
        tech_opinion = await self._get_technical_agent_opinion(symbol, tech_data)
        fundamental_opinion = await self._get_fundamental_agent_opinion(symbol, news_context)
        macro_opinion = await self._get_macro_agent_opinion(symbol, tech_data, news_context)

        # 2. Baş Analist Sentezi
        return await self._get_chief_analyst_synthesis(symbol, tech_opinion, fundamental_opinion, macro_opinion)

    async def _get_technical_agent_opinion(self, symbol: str, data: Dict) -> str:
        prompt = f"""
        Sen bir TEKNİK ANALİZ uzmanısın. {symbol} için şu verileri yorumla:
        RSI: {data.get('rsi', 'N/A')}, Trend: {data.get('trend', 'N/A')}, Karar: {data.get('decision', 'N/A')}.
        Sadece teknik göstergelere odaklanarak 1 cümlelik keskin bir yorum yap.
        """
        return self._generate(prompt)

    async def _get_fundamental_agent_opinion(self, symbol: str, news: List[Dict]) -> str:
        news_text = "\n".join([f"- {n.get('title')}" for n in news[:3]])
        prompt = f"""
        Sen bir TEMEL ANALİZ ve HABER uzmanısın. {symbol} için şu haberleri yorumla:
        {news_text if news else 'Güncel haber bulunmuyor.'}
        Haber akışının piyasa algısına etkisini 1 cümle ile özetle.
        """
        return self._generate(prompt)

    async def _get_macro_agent_opinion(self, symbol: str, data: Dict, news: List[Dict]) -> str:
        prompt = f"""
        Sen bir MAKRO EKONOMİSTSİN. {symbol} ve genel piyasa riski hakkında yorum yap.
        Veriler: Teknik Skor {data.get('score', 50)}, Haber Sayısı: {len(news)}.
        Genel pazar konjonktürü ve risk iştahı açısından 1 cümlelik yorum yap.
        """
        return self._generate(prompt)

    async def _get_chief_analyst_synthesis(self, symbol: str, tech: str, fundamental: str, macro: str) -> str:
        prompt = f"""
        Sen Methefor Finansal Özgürlük sisteminin BAŞ ANALİSTİSİN.
        Aşağıdaki uzman görüşlerini harmanlayarak kullanıcı için 2-3 cümlelik, profesyonel ve etkileyici bir analiz raporu yaz.
        
        TEKNİK GÖRÜŞ: {tech}
        TEMEL GÖRÜŞ: {fundamental}
        MAKRO GÖRÜŞ: {macro}
        
        Dil: Türkçe. Yatırım tavsiyesi içermesin. Odak: {symbol}.
        """
        return self._generate(prompt)

    def _generate(self, prompt: str) -> str:
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Agent Generation Error: {e}")
            return "Veri işlenemedi."

multi_agent_system = MultiAgentSystem()
