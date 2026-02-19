"""
Social Media Generator for Universe 2200

Generates simulated social media feed with citizen reactions, faction propaganda,
and emergent narratives. Deterministic based on seed.
"""

import random
import math
from typing import Dict, List, Any, Optional

class SocialMediaGenerator:
    """
    Generates a feed of social media posts reacting to the world state.
    """
    
    def __init__(self, llm_client=None):
        self.factions = ["Corporate", "Civic", "Shadow", "State"]
        self.llm_client = llm_client
        
    def generate_feed(self, 
                     world_metrics: Dict[str, float],
                     latest_news: List[Dict],
                     seed: int,
                     platform: str = "x", # 'x' or 'insta'
                     count_range: tuple = (5, 15),
                     users: List[Dict] = None) -> Dict[str, List[Dict]]:
        """
        Generate a list of social media posts for a specific platform.
        If 'users' list is provided, acts as real citizens.
        """
        rng = random.Random(seed)
        
        # Determine number of posts
        num_posts = rng.randint(*count_range)
        posts = []
        
        # Extract metrics
        unrest = world_metrics.get('public_unrest', 0.5)
        trust = world_metrics.get('media_trust', 0.5)
        noise = world_metrics.get('information_noise', 0.5)
        
        # Analyze context from news
        news_context = self._analyze_news_context(latest_news)
        
        # [NEW] Try AI Generation first (100% if available)
        if self.llm_client: # Always use AI if client is available
            try:
                ai_posts_data = self._generate_ai_posts(num_posts, world_metrics, news_context, list(post_rng.getstate()))
                if ai_posts_data:
                    return {"posts": ai_posts_data}
            except Exception as e:
                print(f"AI Social Gen failed (fallback to properties): {e}")

        # Fallback / Deterministic Loop
        
        if self.llm_client and users: # Use AI with Real Users
             try:
                ai_posts_data = self._generate_ai_posts_real_users(num_posts, world_metrics, news_context, list(post_rng.getstate()), users)
                if ai_posts_data:
                    return {"posts": ai_posts_data}
             except Exception as e:
                print(f"AI Social Gen failed (fallback): {e}")

        # Fallback / Deterministic Loop
        
        for i in range(num_posts):
            # Deterministic post seed
            post_seed = seed + i * 7919
            post_rng = random.Random(post_seed)
            
            author_user = None
            if users:
                author_user = post_rng.choice(users)
                author_type = author_user.get("role", "citizen")
                # Normalize types for templates
                if author_type not in ["influencer", "media", "faction", "bot", "troll", "comedian"]:
                    author_type = "citizen"
            else:
                # Select Author Type based on Platform & Metrics (Legacy)
                author_type = self._select_author_type(unrest, platform, post_rng)
            
            # Generate ID
            post_id = f"{platform}_{seed}_{i}"
            
            # Generate Platform Specific Content
            if platform == "x":
                content_data = self._generate_x_content(author_type, news_context, world_metrics, post_rng)
            else:
                content_data = self._generate_insta_content(author_type, news_context, world_metrics, post_rng)
                
            # Calculate Engagement
            engagement = self._calculate_engagement(author_type, "neutral", unrest, noise, rng=post_rng)
            
            post = {
                "id": post_id,
                "platform": platform,
                "author_type": author_type,
                "timestamp": f"Tick+{i*2}m",
                "engagement": engagement,
                **content_data
            }
            
            # Inject Real User Data
            if author_user:
                post["author_id"] = author_user.get("id")
                post["author_handle"] = author_user.get("handle")
                post["author_avatar"] = author_user.get("avatar")
                post["author_name"] = author_user.get("display_name")
            
            posts.append(post)
            
        return {"posts": posts}

    def _select_author_type(self, unrest: float, platform: str, rng: random.Random) -> str:
        """Select author type based on world state and platform."""
        # Baseline probabilities
        weights = {
            "citizen": 50,
            "influencer": 5,
            "faction": 15,
            "media": 10,
            "bot": 10,
            "troll": 5,
            "comedian": 5
        }
        
        # Platform adjustments
        if platform == "insta":
            weights["influencer"] += 20
            weights["citizen"] += 10
            weights["faction"] -= 10
            weights["troll"] -= 5 # Less trolling on insta? debatable
            
        if platform == "x":
            weights["troll"] += 10
            weights["bot"] += 10
            weights["media"] += 10
            
        # World State Adjustments
        if unrest > 0.7:
            weights["citizen"] += 10
            weights["bot"] += 10
            
        types = list(weights.keys())
        probs = [weights[t] for t in types]
        return rng.choices(types, weights=probs, k=1)[0]

    def _generate_x_content(self, author_type: str, context: str, metrics: Dict, rng: random.Random) -> Dict:
        """Generate text-heavy content for X."""
        templates = {
            "influencer": [
                "Yeni koleksiyon çıktı. Link biyoda. #siberpunkmoda",
                "Neden herkes bu kadar negatif? Sadece iyi hisler ✨",
                "@CorpTech ile iş birliği çok yakında!",
                "Dürüst olmak gerekirse, Sektör 4'ün ışıklandırması en iyisi."
            ],
            "troll": [
                "L + oran + implantın yok.",
                "2200'de medyaya güvenmek mi? 💀",
                "Kimse sormadı.",
                "Bu olmamış şef.",
                "Ölü internet teorisi gerçek ve hepiniz botsunuz."
            ],
            "comedian": [
                "Otomatik evcil hayvanım sendikalaşmaya çalıştı.",
                "2200'de flört etmek sadece kredi puanlarını karşılaştırmaktan ibaret.",
                "Buna kim 'Siberpunk' dedi, 'Yüksek Teknoloji Sefil Hayat' değil miydi?",
                "Keşke anksiyetemi sürücülerimi güncellediğim kadar kolay güncelleyebilsem."
            ],
            "citizen": [
                "Bugün trafik berbat.",
                "O yüksek sesi duyan oldu mu?",
                "Sadece uygun fiyatlı sentetik et istiyorum.",
                "Çalış, uyu, şarj ol, tekrar et."
            ],
            "faction": [
                "Birlik güçtür.",
                "Doğrulanmış anormallikleri bildirin.",
                "Gelecek güvende.",
                "Uyum güvenliği sağlar."
            ],
            "media": [
                "SON DAKİKA: Piyasa oynaklığı tespit edildi.",
                "Hava durumu uyarısı: Asit yağmuru bekleniyor.",
                "Optiklerinizi yükseltmenin en iyi 10 yolu.",
                "Bu gece Direktör ile röportaj."
            ],
            "bot": [
                "Kripto srip'i şimdi al! %500 kazanç!",
                "[OTO-YANIT] Mesaj alındı.",
                "#Trend #Viral #Haber",
                "Ücretsiz krediler için buraya tıkla."
            ]
        }
        
        # Fallback
        options = templates.get(author_type, templates["citizen"])
        text = rng.choice(options)
        
        # Context Injection
        if rng.random() < 0.3:
            if context == "unrest": text += " Dışarıda güvende kalın."
            if context == "trust": text += " Okuduğunuz her şeye inanmayın."
            
        return {
            "content": text,
            "hashtags": ["#2200", f"#{context}"],
            "is_thread": rng.random() < 0.1
        }

    def _generate_insta_content(self, author_type: str, context: str, metrics: Dict, rng: random.Random) -> Dict:
        """Generate visual-heavy content for Insta."""
        
        visual_prompts = {
            "influencer": "Selfie with neon lights, perfect skin, futuristic fashion",
            "citizen": "Blurry photo of street food, rain on window, cat",
            "media": "Infographic about stock market, weather map",
            "faction": "Propaganda poster, clean minimalist logo",
            "bot": "Generic stock image of cityscape, glitchy artifact",
            "comedian": "Meme image, reaction face",
            "troll": "Screenshot of an argument, low quality wojak meme"
        }
        
        captions = {
            "influencer": ["En iyi hayatımı yaşıyorum ✨", "Filtreye gerek yok", "Rüyalar şehri 🌃", "Mod."],
            "citizen": ["Pazartesi sendromu.", "Rahatlatıcı yemek.", "Manzara.", "Benim küçük sığınağım."],
            "faction": ["Güç.", "Düzen.", "İlerleme.", "Görev."],
            "media": ["Güncelleme.", "devamı için kaydır ->", "Link biyoda.", "Günlük brifing."],
            "bot": ["Daha fazlası için takip et.", "Harika manzara!", "Buna bir bak.", "Vay canına."],
            "comedian": ["Şu an ben.", "Bu neden bu kadar doğru?", "Bir arkadaşını etiketle.", "Lol."],
            "troll": ["Utanç verici.", "Şuna bak.", "Bunu kim yaptı?", "💀"]
        }
        
        prompt = visual_prompts.get(author_type, "Cyberpunk city scene")
        caption = rng.choice(captions.get(author_type, ["..."]))
        
        return {
            "image_prompt": prompt, # For potential AI image gen
            "caption": caption,
            "location": f"Sector {rng.randint(1,9)}",
            "filter": rng.choice(["Neon", "Noir", "Vintage", "Glitch", "None"])
        }

    def _analyze_news_context(self, news: List[Dict]) -> str:
        """Extract dominant theme from latest news."""
        if not news:
            return "general"
        
        # Simple keyword matching on titles
        text = " ".join([n.get('title', '') + " " + n.get('summary', '') for n in news]).lower()
        
        if "unrest" in text or "riot" in text or "compliance" in text:
            return "unrest"
        elif "trust" in text or "media" in text or "fake" in text:
            return "trust"
        elif "surveillance" in text or "monitoring" in text or "privacy" in text:
            return "surveillance"
        elif "corporate" in text or "market" in text or "economy" in text:
            return "corporate"
        
        return "general"
        
    def _calculate_engagement(self, author_type: str, tone: str, unrest: float, 
                             noise: float, rng: random.Random) -> Dict:
        """Calculate simulated engagement stats."""
        base_likes = rng.randint(0, 100)
        base_comments = rng.randint(0, 20)
        base_shares = rng.randint(0, 10)
        
        multiplier = 1.0
        if author_type == "influencer": multiplier = 50.0
        if author_type == "media": multiplier = 20.0
        if author_type == "faction": multiplier = 10.0
        if author_type == "troll" and rng.random() < 0.2: multiplier = 5.0 # viral troll
        
        return {
            "likes": int(base_likes * multiplier),
            "comments": int(base_comments * multiplier * 0.5),
            "shares": int(base_shares * multiplier * 0.3)
        }

    def _select_tone(self, author_type: str, unrest: float, trust: float, rng: random.Random) -> str:
        # User legacy tone selection logic if needed, or remove if fully replaced
        return "neutral"
        
    def _generate_content(self, author_type: str, tone: str, context: str, 
                         metrics: Dict[str, float], rng: random.Random) -> str:
        # Legacy method kept for compatibility if needed, but unused in new flow
        return "Legacy Content"
        
    def _calculate_sentiment(self, tone: str, author_type: str, rng: random.Random) -> float:
        return 0.0

    def _generate_ai_posts(self, count: int, metrics: Dict, context: str, seed_state) -> List[Dict]:
        """Generate posts using LLM."""
        
        system_prompt = (
            "Sen Universe 2200 evreni için bir sosyal medya simülatörüsün. "
            f"Mevcut dünya durumunu yansıtan {count} adet sosyal medya gönderisi oluştur. "
            "Farklı sesler kullan: Vatandaşlar (alaycı/umutlu), Şirket Botları (propaganda), Fenomenler (kibirli), Yeraltı (asi). "
            "YASAKLI KELİMELER (Asla kullanma): neon, glitch, siber, cyber, synth, retro, hologram. "
            "Daha yerel ve distopik argolar kullan: 'çip', 'kredi', 'bölge', 'senkron', 'şebeke'. "
            "Dil: Türkçe. "
            "Sadece JSON çıktısı ver."
        )
        
        user_prompt = f"""
        Dünya Durumu:
        - Huzursuzluk: {metrics.get('public_unrest', 0.5):.2f}/1.0
        - Medya Güveni: {metrics.get('media_trust', 0.5):.2f}/1.0
        - Şirket Gücü: {metrics.get('corp_power_index', 0.5):.2f}/1.0
        - Bağlam teması: {context}
        
        İstenen JSON Yapısı:
        {{
            "posts": [
                {{
                    "platform": "x" veya "insta",
                    "author_type": "citizen|influencer|faction|bot|troll",
                    "content": "metin (X için) veya açıklama (Insta için)",
                    "image_prompt": "görsel tarifi (sadece insta için, yoksa null)",
                    "engagement_level": "low|medium|high|viral"
                }}
            ]
        }}
        """
        
        response = self.llm_client.generate_json(system_prompt, user_prompt)
        
        if not response or 'posts' not in response:
            return None
            
        # Post-process to match internal structure
        final_posts = []
        rng = random.Random() # Local rng for ID generation
        
        for i, p in enumerate(response['posts']):
            platform = p.get('platform', 'x').lower()
            if platform not in ['x', 'insta']: platform = 'x'
            
            # Map engagement level to numbers
            eng_level = p.get('engagement_level', 'medium')
            likes = random.randint(0, 50)
            if eng_level == 'low': likes = random.randint(0, 50)
            if eng_level == 'medium': likes = random.randint(50, 500)
            if eng_level == 'high': likes = random.randint(500, 5000)
            if eng_level == 'viral': likes = random.randint(5000, 50000)
            
            final_posts.append({
                "id": f"ai_{platform}_{random.randint(1000,9999)}_{i}",
                "platform": platform,
                "author_type": p.get('author_type', 'citizen'),
                "timestamp": f"Tick+{i}m",
                "engagement": {
                    "likes": likes,
                    "comments": int(likes * 0.1),
                    "shares": int(likes * 0.05)
                },
                "content": p.get('content'),
                "image_prompt": p.get('image_prompt'),
                "is_ai_generated": True  # Marker for user verification
            })
            
        return final_posts
    def _generate_ai_posts_real_users(self, count: int, metrics: Dict, context: str, seed_state, users: List[Dict]) -> List[Dict]:
        """Generate posts using AI representing SPECIFIC users."""
        
        # Pick N users
        rng = random.Random() 
        selected_users = rng.sample(users, min(len(users), count))
        
        user_profiles_str = ""
        for i, u in enumerate(selected_users):
            user_profiles_str += (
                f"User {i+1}: Handle: {u.get('handle')}, Role: {u.get('role')}, "
                f"Faction: {u.get('faction')}, Traits: {', '.join(u.get('traits', []))}\n"
            )
        
        system_prompt = (
            "Sen Universe 2200 evreni için bir sosyal medya motorusun. "
            "Sana verilen GERÇEK vatandaş profillerini kullanarak, onların ağzından atılmış tweetler/postlar üret. "
            "Kişinin rolüne (Influencer, Gazeteci, Vatandaş) ve faction'ına (Corporate, Civic, vb.) uygun konuş. "
            "Argo, yerel terimler (kredi, bölge, çip) kullan. "
            "Format: JSON listesi."
        )
        
        user_prompt = f"""
        Bağlam: {context} (Huzursuzluk: {metrics.get('public_unrest', 0.5):.2f})
        
        Seçilen Kullanıcılar:
        {user_profiles_str}
        
        İstenen JSON Yapısı:
        {{
            "posts": [
                {{
                    "user_index": 0, // Yukarıdaki listedeki sıra no (1-based değil 0-based index)
                    "platform": "x",
                    "content": "Post içeriği...",
                    "image_prompt": "görsel tarifi (opsiyonel)"
                }}
            ]
        }}
        """
        
        response = self.llm_client.generate_json(system_prompt, user_prompt)
        if not response or 'posts' not in response:
            return None
            
        final_posts = []
        for p in response['posts']:
            try:
                idx = p.get('user_index', 0)
                if idx >= len(selected_users): continue
                
                user = selected_users[idx]
                platform = "x"
                
                # Engagement sim
                likes = random.randint(0, 500)
                if user.get("role") == "influencer": likes *= 10
                
                final_posts.append({
                    "id": f"post_{user['id']}_{random.randint(1000,9999)}",
                    "platform": platform,
                    "author_id": user['id'],
                    "author_handle": user['handle'],
                    "author_name": user['display_name'],
                    "author_avatar": user['avatar'],
                    "author_type": user.get('role', 'citizen'),
                    "timestamp": datetime.now().isoformat(),
                    "engagement": {
                        "likes": likes,
                        "comments": int(likes * 0.1),
                        "shares": int(likes * 0.05)
                    },
                    "content": p.get('content'),
                    "image_prompt": p.get('image_prompt'),
                    "is_ai_generated": True
                })
            except Exception as e:
                print(f"Skipping post gen error: {e}")
                continue
                
        return final_posts
