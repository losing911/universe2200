"""
Dystopian News Generator for Universe 2200

Generates realistic, semi-neutral news articles with dystopian undertones.
All outputs are deterministic based on seeded random generation.
"""

import random
from typing import Dict, Any


def generate_news(event: Dict[str, Any], world_metrics: Dict[str, float], seed: int, **kwargs) -> Dict[str, Any]:
    """
    Generate a dystopian news article based on world state and event.
    
    Args:
        event: Event dictionary with 'type', 'severity', 'value'
        world_metrics: World state metrics dictionary
        seed: Random seed for deterministic generation
        
    Returns:
        Dictionary with headline, summary, bias_score, impact_level
    """
    # Create seeded RNG for determinism
    rng = random.Random(seed)
    
    # extract key metrics
    unrest = world_metrics.get('public_unrest', 0.5)
    trust = world_metrics.get('media_trust', 0.5)
    surveillance = world_metrics.get('surveillance_level', 0.5)
    corp_power = world_metrics.get('corp_power_index', 0.5)
    
    # Determine bias based on metrics
    bias_score = (surveillance + corp_power - unrest - (1 - trust)) / 4
    bias_score = max(-1.0, min(1.0, bias_score))
    
    event_type = event.get('type', 'unknown')
    severity = event.get('severity', 'medium')
    value = event.get('value', 0.5)
    
    # Try AI generation if client is provided
    # Note: caller must pass 'llm_client' in kwargs
    # We use **kwargs to capture optional arguments without breaking signature
    llm_client = kwargs.get('llm_client')
    
    if llm_client:
        try:
            ai_article = _generate_ai_news(llm_client, event, world_metrics, bias_score)
            if ai_article:
                return ai_article
        except Exception as e:
            # Fallback to templates on error
            print(f"AI Generation failed: {e}")
            pass

    # Template fallback
    templates = _generate_headline(event_type, severity, value, unrest, bias_score, rng)
    summary = _generate_summary(event_type, severity, value, world_metrics, bias_score, rng)
    impact_level = _determine_impact(severity, value, unrest)
    
    return {
        "headline": templates,
        "summary": summary,
        "bias_score": round(bias_score, 2),
        "impact_level": impact_level,
        "event_type": event_type,
        "severity": severity,
        "source": "State Media" if bias_score > 0.3 else "Underground" if bias_score < -0.3 else "Independent"
    }

def _generate_ai_news(client, event, metrics, bias_score):
    """Generate news using LLM."""
    system_prompt = (
        "Sen Universe 2200 evreni için distopik haber üreten bir muhabirsin. "
        "Sadece JSON formatında çıktı ver. "
        "Dil: Türkçe. "
        "Ton: Ciddi, hafif karanlık, gerçekçi distopya. "
        "YASAKLI KELİMELER (Asla kullanma): neon, glitch, siber, cyber, synth, retro, hologram. "
        "Bu kelimeler yerine daha organik, bürokratik veya endüstriyel terimler kullan."
    )
    
    user_prompt = f"""
    Olay: {event.get('type')} (Ciddiyet: {event.get('severity')})
    Detaylar: Huzursuzluk={metrics.get('public_unrest'):.2f}, Güven={metrics.get('media_trust'):.2f}, Gözetim={metrics.get('surveillance_level'):.2f}
    Önyargı Skoru: {bias_score:.2f} (-1.0 = muhalif, 1.0 = devlet yanlısı)
    
    İstenen JSON Yapısı:
    {{
        "headline": "Çarpıcı bir başlık",
        "summary": "2-3 cümlelik özet",
        "bias_score": float,
        "impact_level": "low|medium|high|critical",
        "event_type": "string",
        "severity": "string",
        "source": "Devlet Medyası|Yeraltı|Bağımsız"
    }}
    """
    
    return client.generate_json(system_prompt, user_prompt)



def _generate_headline(event_type: str, severity: str, value: float, 
                       unrest: float, bias: float, rng: random.Random) -> str:
    """Generate dystopian headline based on event."""
    
    headline_templates = {
        "unrest_critical": [
            "Huzursuzluk Endeksi Tavan Yaptı: Kamu Düzeni Protokolleri Devrede",
            "Sivil Uyum Endeksi Kritik Eşiğin Altına Düştü",
            "Yetkililer Gelişmiş Barış Gücü Önlemlerini Devreye Aldı",
            "Toplumsal İstikrar Çerçevesi Benzeri Görülmemiş Bir Baskı Altında"
        ],
        "unrest_spike": [
            "Artan Hoşnutsuzluk Devlet Müdahalesini Tetikledi",
            "Kamuoyu Analizleri Artan Gerilimi Ortaya Koyuyor",
            "Güvenlik Altyapısı Huzursuzluk Göstergelerine Karşı Ölçeklendiriliyor",
            "Sivil Katılım Modelleri Uyumsuzluğa Doğru Kayıyor"
        ],
        "trust_lost": [
            "Bilgi Doğrulama Sistemleri Tam Güven Çöküşü Bildiriyor",
            "Kurumsal Kanallara Olan Kamu Güveni Tarihi Düşük Seviyede",
            "Medya Güvenilirlik Endeksi Kritik Arıza Moduna Girdi",
            "Vatandaşlar Resmi Bilgi Kaynaklarını Giderek Daha Fazla Reddediyor"
        ],
        "trust_collapse": [
            "Güven Metrikleri Medya İtimadında Hızlanan Düşüşü Gösteriyor",
            "Bilgi Ekosistemi Parçalanması Şiddetleniyor",
            "Resmi Anlatılara Yönelik Kamuoyu Şüpheciliği Artıyor",
            "Kurumsal Güvenilirlik Puanları Sürdürülebilir Seviyelerin Altına Düştü"
        ],
        "surveillance_state": [
            "Gelişmiş İzleme Sistemleri Tam Dağıtıma Ulaştı",
            "Güvenlik Altyapısı Genişlemesi Tamamlandı İlan Edildi",
            "Kamu Güvenliği Ağı Maksimum Kapsama Alanına Ulaştı",
            "Davranışsal Analitk Entegrasyonu Son Aşamaya Girdi"
        ],
        "corporate_dominance": [
            "Özel Sektörün Politika Çerçeveleri Üzerindeki Etkisi Genişliyor",
            "Ekonomik Varlıklar Daha Fazla Yönetim İşlevi Üstleniyor",
            "Şirket-Devlet Ortaklık Modeli Standart Hale Geldi",
            "Piyasa Güçleri İdari Yapıları Yeniden Şekillendiriyor"
        ],
        "information_chaos": [
            "Veri Aşırı Yükleme Metrikleri İşleme Eşiklerini Aştı",
            "Bilgi Doğrulama Kapasitesi Hacim Artışıyla Mücadele Ediyor",
            "Sinyal-Gürültü Oranları Kritik Tersine Çevrilme Noktasına Ulaştı",
            "Gerçek-Kontrol Sistemleri Hacim Dalgasıyla Mücadele Ediyor"
        ],
        "systemic_crisis": [
            "Çoklu Sistem Arızaları Benzeri Görülmemiş İstikrarsızlık Yaratıyor",
            "Zincirleme Olaylar Acil Durum Protokolü Aktivasyonunu Tetikledi",
            "Altyapı Dayanıklılık Testleri Kritik Zafiyetleri Ortaya Çıkardı",
            "Eş zamanlı Zorluklar Müdahale Yeteneklerini Zorluyor"
        ]
    }
    
    templates = headline_templates.get(event_type, [
        "Metropol Sektörlerinde Önemli Gelişmeler Bildiriliyor",
        "Yetkililer Gelişen Durumu İzliyor",
        "Devlet Sistemleri Ortaya Çıkan Koşullara Yanıt Veriyor"
    ])
    
    # Select deterministically based on RNG
    return rng.choice(templates)


def _generate_summary(event_type: str, severity: str, value: float,
                     metrics: Dict[str, float], bias: float, rng: random.Random) -> str:
    """Generate multi-sentence summary with dystopian realism."""
    
    # Extract metrics
    unrest = metrics.get('public_unrest', 0.5)
    trust = metrics.get('media_trust', 0.5)
    surveillance = metrics.get('surveillance_level', 0.5)
    
    summary_templates = {
        "unrest_critical": [
            f"Devlet izleme sistemleri, kamu huzursuzluğu seviyesini {value:.2f} olarak tespit etti ve otomatik yanıt protokollerini tetikledi. "
            f"Yetkililer, artırılmış güvenlik önlemlerinin geçici doğasını vurguluyor. "
            f"Vatandaşların sivil düzen direktiflerine uymaları tavsiye ediliyor. "
            f"Bağımsız gözlemciler, metropol bölgelerinde isyan kontrol altyapısının konuşlandırıldığını belirtiyor.",
            
            f"Huzursuzluk endeksi bugün {value:.2f} seviyesine ulaşarak yetkilileri acil durum yönetim prosedürlerini etkinleştirmeye yöneltti. "
            f"Belirlenen eşikleri aşan halka açık toplanmalar artık özel izin gerektiriyor. "
            f"Devlet medyası, istikrar protokollerinin normal operasyonları geri getireceği konusunda vatandaşlara güvence veriyor. "
            f"Ancak, şifreli iletişimler resmi anlatılara karşı yaygın bir şüphecilik olduğunu gösteriyor."
        ],
        "trust_collapse": [
            f"Medya güven metrikleri {value:.2f} seviyesine düştü, bu da kamu güveninde %{(1-value)*100:.0f} oranında bir erozyonu temsil ediyor. "
            f"Kurumsal sözcüler bunu koordineli dezenformasyon kampanyalarına bağlıyor. "
            f"Yanlış anlatılarla mücadele etmek için yeni doğrulama çerçeveleri devreye alınıyor. "
            f"Eleştirmenler, önlemlerin güvenilirliğin azalmasına katkıda bulunduğunu savunuyor.",
            
            f"Bilgi kanallarına olan halk inancı, güven endeksinde {value:.2f} seviyesine çöktü. "
            f"Devlet destekli doğrulama girişimleri sınırlı etkinlik bildiriyor. "
            f"Alternatif medya platformları etkileşimde artış yaşıyor. "
            f"Yetkililer, içerik düzenleme protokollerini devreye alırken doğrulanmamış kaynaklara karşı uyarıda bulunuyor."
        ],
        "surveillance_state": [
            f"Gözetim kapsama endeksi şu anda {value:.2f} seviyesinde duruyor ve neredeyse tam uygulamayı işaret ediyor. "
            f"Gizlilik savunuculuğu grupları, düzenleyici uyum başarısızlıklarının ardından dağıldı. "
            f"Yetkililer, genişlemenin gerekçesi olarak suç azaltma istatistiklerini öne sürüyor. "
            f"Davranış tahmin algoritmaları, vatandaş aktivitesi tahmininde %87 doğruluk oranı elde ediyor.",
            
            f"İzleme altyapısı, kentsel merkezlerde {value:.2f} doygunluğuna ulaştı. "
            f"Her kamusal alan artık entegre sensör ağları ve biyometrik takip özelliklerine sahip. "
            f"Devlet temsilcileri bunu kamu güvenliği optimizasyonu için gerekli olarak çerçeveliyor. "
            f"Muhalifler, tespitten kaçınmak için giderek daha fazla analog iletişim yöntemlerine güveniyor."
        ],
        "corporate_dominance": [
            f"Şirket etki metrikleri, özel kuruluşların daha fazla yönetim rolü üstlenmesiyle {value:.2f} seviyesine tırmandı. "
            f"Geleneksel hükümet işlevleri giderek daha fazla piyasa tabanlı çözümlere devrediliyor. "
            f"Yapısal yeniden düzenlemenin birincil itici gücü olarak ekonomik verimlilik gösteriliyor. "
            f"Emek savunuculuğu grupları, azalan işçi korumaları konusunda endişelerini dile getiriyor.",
            
            f"Şirket gücü endeksi, benzeri görülmemiş iş-devlet entegrasyonunu yansıtarak {value:.2f} seviyesine ulaştı. "
            f"Politika kararları artık rutin olarak ekonomik optimizasyon modellerine erteleniyor. "
            f"Vatandaşlar, kamu ve özel otorite arasında ayrım yapmakta zorlandıklarını bildiriyor. "
            f"Eleştirmenler, ortaya çıkan hibrit yönetim modelindeki hesap verebilirlik boşlukları konusunda uyarıyor."
        ]
    }
    
    # Get templates or use generic
    templates = summary_templates.get(event_type, [
        f"İzleme sistemleri sosyal metriklerde önemli bir değişkenlik kaydetti. "
        f"Devlet analistleri politika çerçeveleri üzerindeki etkileri değerlendirmeye devam ediyor. "
        f"Vatandaşların normal aktivite modellerini sürdürmeleri teşvik ediliyor. "
        f"Durum geliştikçe daha fazla güncelleme sağlanacaktır."
    ])
    
    # Select deterministically
    return rng.choice(templates)


def _determine_impact(severity: str, value: float, unrest: float) -> str:
    """Determine impact level based on severity and context."""
    
    if severity == "critical":
        return "high"
    elif severity == "high":
        return "high" if value > 0.85 or unrest > 0.85 else "medium"
    else:
        return "medium" if value > 0.5 else "low"


# Example usage
if __name__ == "__main__":
    import json
    
    # Test scenarios
    test_event = {
        "type": "unrest_critical",
        "severity": "critical",
        "value": 0.95
    }
    
    test_metrics = {
        "public_unrest": 0.95,
        "media_trust": 0.15,
        "surveillance_level": 0.85,
        "corp_power_index": 0.75,
        "information_noise": 0.90
    }
    
    # Generate news with seed for determinism
    news = generate_news(test_event, test_metrics, seed=42)
    
    print("=== Dystopian News Generator Test ===")
    print(json.dumps(news, indent=2))
    
    # Test determinism
    news2 = generate_news(test_event, test_metrics, seed=42)
    print(f"\nDeterminism check: {news == news2}")
    
    # Test different event
    trust_event = {
        "type": "trust_collapse",
        "severity": "high",
        "value": 0.18
    }
    
    news3 = generate_news(trust_event, test_metrics, seed=123)
    print("\n=== Trust Collapse Event ===")
    print(json.dumps(news3, indent=2))
