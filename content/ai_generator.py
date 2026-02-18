"""
AI-Based Content Generator (Stub)

Placeholder for future AI-powered content generation.
NOT IMPLEMENTED YET - raises NotImplementedError.
"""

from typing import Dict, Any

from content.generator_base import ContentGeneratorBase
from core.events import Event


class AIContentGenerator(ContentGeneratorBase):
    """
    AI-powered content generator.
    Generates content in Turkish using LLM, avoiding cliché terms.
    """
    
    def __init__(self, llm_client=None):
        """
        Initialize AI content generator.
        
        Args:
            llm_client: Client for LLM interactions
        """
        self.llm_client = llm_client
        self.forbidden_words = ["neon", "glitch", "siber", "cyber", "synth", "retro", "hologram"]
    
    def _check_constraints(self, text: str) -> bool:
        """Check if text contains forbidden words."""
        lower_text = text.lower()
        return not any(word in lower_text for word in self.forbidden_words)

    def generate_news_content(self, event: Event) -> Dict[str, Any]:
        """Generate news content using AI in Turkish."""
        if not self.llm_client:
            raise ValueError("LLM Client not initialized for AIContentGenerator")

        system_prompt = (
            "Sen Universe 2200 evreni için distopik haber üreten bir muhabirsin. "
            "Sadece JSON formatında çıktı ver. "
            "Dil: Türkçe. "
            "Ton: Ciddi, hafif karanlık, gerçekçi distopya. "
            "YASAKLI KELİMELER (Asla kullanma): neon, glitch, siber, cyber, synth, retro, hologram. "
            "Bu kelimeler yerine daha organik, bürokratik veya endüstriyel terimler kullan."
        )
        
        user_prompt = f"""
        Olay: {event.type} (Ciddiyet: {event.severity})
        Detay: {event.description}
        
        İstenen JSON Yapısı:
        {{
            "headline": "Çarpıcı bir başlık",
            "summary": "2-3 cümlelik özet",
            "bias_score": float (-1.0 ile 1.0 arası),
            "impact_level": "low|medium|high|critical",
            "source": "Devlet Medyası|Yeraltı|Bağımsız"
        }}
        """
        
        return self.llm_client.generate_json(system_prompt, user_prompt)
    
    def generate_social_content(self, event: Event) -> Dict[str, Any]:
        """Generate social media content using AI in Turkish."""
        if not self.llm_client:
            raise ValueError("LLM Client not initialized for AIContentGenerator")
            
        system_prompt = (
            "Sen Universe 2200 evreninde yaşayan bir vatandaşsın. "
            "Sosyal medya paylaşımı yapıyorsun. "
            "Sadece JSON formatında çıktı ver. "
            "Dil: Türkçe. "
            "Kullanıcı Tipi: Vatandaş, Kurumsal Bot veya Muhalif. "
            "YASAKLI KELİMELER: neon, glitch, siber, cyber, synth, retro, hologram. "
            "Daha çok 'sistem', 'altyapı', 'denetim', 'kod', 'veri' gibi terimler kullan."
        )
        
        user_prompt = f"""
        Olay: {event.type}
        
        İstenen JSON Yapısı:
        {{
            "content": "Kısa sosyal medya metni (max 280 karakter)",
            "hashtags": ["etiket1", "etiket2"],
            "engagement_prediction": "low|medium|high"
        }}
        """
        
        return self.llm_client.generate_json(system_prompt, user_prompt)
    
    def generate_video_content(self, event: Event) -> Dict[str, Any]:
        """Generate video content metadata using AI."""
        # Stub implementation to satisfy interface
        return {
            "title": f"Gelişme: {event.type}",
            "description": "Video kaydı işleniyor...",
            "duration": "0:45"
        }
    
    def generate_market_alert(self, event: Event) -> Dict[str, Any]:
        """Generate market alert using AI."""
        # Stub implementation to satisfy interface
        return {
            "symbol": "GEN",
            "alert": "Piyasa Dalgalanması",
            "advice": "Bekle"
        }
