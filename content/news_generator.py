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
            "Public Order Protocols Activated as Dissent Metrics Spike",
            "Civic Compliance Index Drops to Critical Threshold",
            "Authorities Deploy Enhanced Peacekeeping Measures",
            "Social Stability Framework Under Unprecedented Strain"
        ],
        "unrest_spike": [
            "Rising Discontent Triggers State Response Evaluation",
            "Public Sentiment Analysis Reveals Growing Tensions",
            "Security Infrastructure Scales to Address Unrest Indicators",
            "Civic Engagement Patterns Shift Toward Non-Compliance"
        ],
        "trust_lost": [
            "Information Verification Systems Report Total Confidence Collapse",
            "Public Trust in Institutional Channels Reaches Historic Low",
            "Media Credibility Index Enters Critical Failure Mode",
            "Citizens Increasingly Reject Official Information Sources"
        ],
        "trust_collapse": [
            "Trust Metrics Show Accelerating Decline in Media Confidence",
            "Information Ecosystem Fragmentation Intensifies",
            "Public Skepticism of Official Narratives Surges",
            "Institutional Credibility Scores Drop Below Sustainable Levels"
        ],
        "surveillance_state": [
            "Enhanced Monitoring Systems Achieve Full Deployment",
            "Security Infrastructure Expansion Declared Complete",
            "Public Safety Network Reaches Maximum Coverage",
            "Behavioral Analytics Integration Enters Final Phase"
        ],
        "corporate_dominance": [
            "Private Sector Influence on Policy Frameworks Expands",
            "Economic Entities Assume Greater Governance Functions",
            "Corporate-State Partnership Model Becomes Standard",
            "Market Forces Reshape Administrative Structures"
        ],
        "information_chaos": [
            "Data Overload Metrics Exceed Processing Thresholds",
            "Information Verification Capacity Overwhelmed",
            "Signal-to-Noise Ratios Reach Critical Inversion",
            "Fact-Checking Systems Struggle with Volume Surge"
        ],
        "systemic_crisis": [
            "Multiple System Failures Create Unprecedented Instability",
            "Cascade Events Trigger Emergency Protocol Activation",
            "Infrastructure Resilience Tests Reveal Critical Vulnerabilities",
            "Simultaneous Challenges Strain Response Capabilities"
        ]
    }
    
    templates = headline_templates.get(event_type, [
        "Significant Developments Reported in Metropolitan Sectors",
        "Authorities Monitor Evolving Situation",
        "State Systems Respond to Emerging Conditions"
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
            f"State monitoring systems detected public unrest levels at {value:.2f}, triggering automated response protocols. "
            f"Officials emphasize the temporary nature of enhanced security measures. "
            f"Citizens are advised to maintain compliance with civic order directives. "
            f"Independent observers note the deployment of riot control infrastructure across metropolitan zones.",
            
            f"The unrest index reached {value:.2f} today, prompting authorities to activate emergency governance procedures. "
            f"Public gatherings exceeding designated thresholds now require special authorization. "
            f"State media assures citizens that stability protocols will restore normal operations. "
            f"However, encrypted communications suggest widespread skepticism of official narratives."
        ],
        "trust_collapse": [
            f"Media trust metrics dropped to {value:.2f}, representing a {(1-value)*100:.0f}% erosion of public confidence. "
            f"Institutional spokespeople attribute this to coordinated disinformation campaigns. "
            f"New verification frameworks are being deployed to combat false narratives. "
            f"Critics argue the measures themselves contribute to declining credibility.",
            
            f"Public faith in information channels has collapsed to {value:.2f} on the trust index. "
            f"State-sponsored fact-checking initiatives report limited effectiveness. "
            f"Alternative media platforms experience surge in engagement. "
            f"Authorities warn against unverified sources while rolling out content regulation protocols."
        ],
        "surveillance_state": [
            f"The surveillance coverage index now stands at {value:.2f}, marking near-total implementation. "
            f"Privacy advocacy groups disbanded following regulatory compliance failures. "
            f"Officials tout crime reduction statistics as justification for expansion. "
            f"Behavioral prediction algorithms achieve 87% accuracy in citizen activity forecasting.",
            
            f"Monitoring infrastructure reached {value:.2f} saturation across urban centers. "
            f"Every public space now features integrated sensor networks and biometric tracking. "
            f"State representatives frame this as necessary for public safety optimization. "
            f"Dissidents increasingly rely on analog communication methods to evade detection."
        ],
        "corporate_dominance": [
            f"Corporate influence metrics climbed to {value:.2f} as private entities assume more governance roles. "
            f"Traditional government functions increasingly outsourced to market-based solutions. "
            f"Economic efficiency cited as primary driver of structural reorganization. "
            f"Labor advocacy groups express concern over diminishing worker protections.",
            
            f"The corporate power index hit {value:.2f}, reflecting unprecedented business-state integration. "
            f"Policy decisions now routinely defer to economic optimization models. "
            f"Citizens report difficulty distinguishing between public and private authority. "
            f"Critics warn of accountability gaps in the emerging hybrid governance model."
        ]
    }
    
    # Get templates or use generic
    templates = summary_templates.get(event_type, [
        f"Monitoring systems registered significant variance in social metrics. "
        f"State analysts continue evaluating the implications for policy frameworks. "
        f"Citizens are encouraged to maintain normal activity patterns. "
        f"Further updates will be provided as the situation develops."
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
