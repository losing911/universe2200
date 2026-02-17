# Universe 2200 - Faz 2 Devam Planı

## Özet

Faz 1'de temel simülasyon motorunu, population engine'i, sosyal ağ çekirdeğini ve broadcast API'yi tamamladık. Şu an API production'da çalışıyor (`anxipunk.icu`).

**Faz 2'de yapılacaklar:**
1. **Ideological Pipeline** - Farklı ideolojik bakış açılarından haber üretimi
2. **Archival System** - Haber arşivleme sistemi
3. **Narrative Memory** - Vektör tabanlı hafıza sistemi (AI entegrasyonu)
4. **WebSocket Support** - Real-time updates
5. **API Filtering & Pagination** - Gelişmiş sorgu özellikleri

---

## Kalan İşler (task.md'den)

### Part 2: Ideological Pipeline ❌

**Durum:** Tamamlanmadı

**Hedef:** Her olay için farklı ideolojik perspektiflerden (State, Corporate, Civic, Shadow) haber üretmek.

**Gerekli Dosyalar:**
- `ai_content/chrononet/narratives.py` - İdeoloji profilleri
- `ai_content/chrononet/pipeline.py` - Multi-perspective üretim
- `ai_content/chrononet/generator.py` (güncelleme) - `narrative_profile` parametresi ekle

**Örnek Çıktı:**
```json
{
  "event_id": "protest_001",
  "articles": [
    {
      "ideology": "State",
      "headline": "Unauthorized Gathering Dispersed by Security Forces",
      "tone": "authoritarian"
    },
    {
      "ideology": "Corporate",
      "headline": "Market Volatility Expected Following Protest Activity",
      "tone": "pragmatic"
    },
    {
      "ideology": "Civic",
      "headline": "Citizens Demand Water Access Reform in District 7",
      "tone": "activist"
    },
    {
      "ideology": "Shadow",
      "headline": "Surveillance Grid Fails as Crowds Overwhelm Sensors",
      "tone": "conspiratorial"
    }
  }
}
```

**Implementasyon Adımları:**
1. `narratives.py` oluştur (4 sabit profil tanımla)
2. `ChronoNetGenerator` sınıfına `narrative_profile: str` parametresi ekle
3. `pipeline.py` içinde her olay için 4 farklı versiyon üret
4. JSON output validation ekle

---

### Part 3: Archival System ❌

**Durum:** Tamamlanmadı

**Hedef:** Üretilen haberleri tarihli klasör yapısında arşivlemek.

**Dizin Yapısı:**
```
data/news/
├── 2207/
│   ├── 03/
│   │   ├── 15/
│   │   │   ├── chrononet_protest_state_water-crisis.json
│   │   │   ├── chrononet_protest_corp_water-crisis.json
│   │   │   ├── chrononet_protest_civic_water-crisis.json
│   │   │   └── chrononet_protest_shadow_water-crisis.json
│   │   └── 16/
│   └── 04/
```

**Dosya Formatı:**
- Pattern: `chrononet_{event_type}_{ideology}_{slug}.json`
- `slug`: Başlıktan türetilen URL-safe string (örn: "water-crisis")

**Implementasyon:**
```python
# content/news_archiver.py
import os
from pathlib import Path
from datetime import datetime

class NewsArchiver:
    def __init__(self, base_dir="data/news"):
        self.base_dir = Path(base_dir)
    
    def save_article(self, article: dict, sim_date: str):
        # sim_date format: "2207-03-15"
        year, month, day = sim_date.split('-')
        
        # Create directory
        dir_path = self.base_dir / year / month / day
        dir_path.mkdir(parents=True, exist_ok=True)
        
        # Generate filename
        slug = self._create_slug(article['headline'])
        filename = f"chrononet_{article['event_type']}_{article['ideology']}_{slug}.json"
        
        # Save
        with open(dir_path / filename, 'w') as f:
            json.dump(article, f, indent=2)
    
    def _create_slug(self, headline: str) -> str:
        import re
        slug = headline.lower()
        slug = re.sub(r'[^a-z0-9]+', '-', slug)
        return slug[:50]  # Max 50 karakter
```

---

### Part 4: Integration ❌

**Durum:** Kısmen tamamlandı (ContentPipeline var ama ideological pipeline yok)

**Hedef:** Ideological Pipeline'ı simülasyon loop'una entegre et.

**Değiştirilecek Dosya:** `core/content_pipeline.py`

```python
# Mevcut: Tek perspektif haber
def generate_news(self, world_state):
    news = self.news_generator.generate(world_state)
    # Save to data/public/public_news.json
    
# Yeni: Multi-perspektif haber
def generate_news(self, world_state):
    events = self._detect_events(world_state)
    
    all_articles = []
    for event in events:
        # Her olay için 4 perspektif
        articles = self.news_pipeline.generate_multi_perspective(event)
        all_articles.extend(articles)
        
        # Arşivle
        for article in articles:
            self.archiver.save_article(article, world_state.current_date)
    
    # Public API için sadece en önemli birkaç tanesi
    public_news = self._select_top_articles(all_articles, limit=10)
    self._write_public(public_news)
```

---

### Part 8: Narrative Memory Integration ❌

**Durum:** Tamamlanmadı

**Hedef:** Population Engine'in ürettiği yorumları ve haberleri vektör tabanlı hafızada saklamak.

**Kullanım Durumu:**
- AI reply generator, yorumlara cevap verirken context için hafızayı sorgular
- Haber generator, benzer olayları hatırlayıp referans verir
- Social network, trend detection için hafızayı kullanır

**Implementasyon (Mock):**
```python
# core/narrative_memory.py
import numpy as np
from typing import List, Dict

class NarrativeMemory:
    """Mock vector store - Phase 2'de gerçek embedding kullanılacak."""
    
    def __init__(self):
        self.memories = []  # List of (text, embedding, metadata)
    
    def add(self, text: str, metadata: dict):
        # Mock embedding (gerçekte OpenAI/Cohere embedding API kullanılacak)
        embedding = self._mock_embed(text)
        self.memories.append({
            'text': text,
            'embedding': embedding,
            'metadata': metadata
        })
    
    def retrieve_context(self, query: str, top_k: int = 5) -> List[Dict]:
        # Mock similarity search
        query_emb = self._mock_embed(query)
        
        # Basit keyword matching (gerçekte cosine similarity)
        results = []
        for mem in self.memories:
            score = self._keyword_similarity(query, mem['text'])
            results.append((score, mem))
        
        # Top k döndür
        results.sort(reverse=True, key=lambda x: x[0])
        return [mem for score, mem in results[:top_k]]
    
    def _mock_embed(self, text: str):
        # Basit hash-based embedding
        return hash(text) % 1000
    
    def _keyword_similarity(self, a: str, b: str) -> float:
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        return len(words_a & words_b) / max(len(words_a | words_b), 1)
```

**Integration:**
```python
# core/reply_pipeline.py (güncellenecek)
class ReplyPipeline:
    def __init__(self, ..., memory: NarrativeMemory):
        self.memory = memory
        ...
    
    def generate_reply(self, comment: Comment):
        # Hafızadan context çek
        context = self.memory.retrieve_context(comment.content, top_k=3)
        
        # Context ile birlikte reply üret
        reply = self.reply_generator.generate(comment, context)
        
        # Yeni yorumu hafızaya ekle
        self.memory.add(comment.content, {
            'type': 'comment',
            'user_id': comment.user_id,
            'sentiment': comment.sentiment
        })
        
        return reply
```

---

## Faz 2 Öncelik Sırası

1. **Ideological Pipeline** (Part 2) - Haber sitesi için çeşitlilik
2. **Archival System** (Part 3) - Historical data
3. **API Filtering** - Frontend için

**Daha Sonra:**
4. Narrative Memory (Part 8) - AI reply kalitesi için
5. WebSocket - Real-time updates

---

## Faz 2 Zaman Tahmini

| Görev | Süre | Karmaşıklık |
|-------|------|-------------|
| Ideological Pipeline | 2-3 saat | Orta |
| Archival System | 1-2 saat | Düşük |
| API Filtering | 1 saat | Düşük |
| Narrative Memory (Mock) | 2 saat | Orta |
| WebSocket Support | 3-4 saat | Yüksek |

**Toplam:** ~9-12 saat

---

## Başlangıç Noktası (Kod Örnekleri)

### 1. Ideological Pipeline Başlangıç

```python
# ai_content/chrononet/narratives.py
NARRATIVE_PROFILES = {
    "State": {
        "bias": "authoritarian",
        "keywords": ["security", "order", "stability", "compliance"],
        "tone": "official",
        "stance": "pro-government"
    },
    "Corporate": {
        "bias": "capitalist",
        "keywords": ["market", "efficiency", "growth", "profit"],
        "tone": "pragmatic",
        "stance": "pro-business"
    },
    "Civic": {
        "bias": "populist",
        "keywords": ["rights", "justice", "equality", "reform"],
        "tone": "activist",
        "stance": "pro-people"
    },
    "Shadow": {
        "bias": "conspiratorial",
        "keywords": ["surveillance", "control", "truth", "hidden"],
        "tone": "suspicious",
        "stance": "anti-establishment"
    }
}

def get_profile(ideology: str) -> dict:
    return NARRATIVE_PROFILES.get(ideology, NARRATIVE_PROFILES["Civic"])
```

```python
# ai_content/chrononet/pipeline.py
from .narratives import get_profile, NARRATIVE_PROFILES
from .generator import ChronoNetGenerator

class IdeologicalPipeline:
    def __init__(self):
        self.generator = ChronoNetGenerator()
    
    def generate_multi_perspective(self, event: dict) -> list:
        articles = []
        
        for ideology in NARRATIVE_PROFILES.keys():
            profile = get_profile(ideology)
            
            # Generator'a profile ile çağrı yap
            article = self.generator.generate_article(
                event=event,
                narrative_profile=profile
            )
            
            article['ideology'] = ideology
            articles.append(article)
        
        return articles
```

### 2. API Filtering Başlangıç

```python
# api/broadcast_api.py (güncellenecek)
from fastapi import Query

@app.get("/api/news")
async def get_news(
    category: str = Query(None, description="Filter by category"),
    severity: str = Query(None, description="Filter by severity"),
    limit: int = Query(10, ge=1, le=100)
):
    news = load_news_data()
    
    # Filter
    if category:
        news = [n for n in news if n.get('category') == category]
    if severity:
        news = [n for n in news if n.get('severity') == severity]
    
    # Limit
    news = news[:limit]
    
    return {"status": "success", "data": news, "count": len(news)}
```

---

## Sonraki Adımlar

1. **API Integration Guide'ı** haber/sosyal medya sitesi projesinde kullan.
2. **Faz 2'ye başla** - Önce "Ideological Pipeline" kısmını kodla.
3. **Test et** - Her yeni feature production'a pushlayıp `anxipunk.icu` üzerinde doğrula.

Hangi kısımdan başlamak istersiniz?
