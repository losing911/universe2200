# Universe 2200 - API Entegrasyon Kılavuzu

## Genel Bakış

Universe 2200, sürekli çalışan bir simülasyon motoru ve REST API'dir. Evren içinde olaylar, sosyal medya aktiviteleri, haber başlıkları otomatik olarak üretilir ve API üzerinden haber siteleri veya sosyal medya platformları tarafından tüketilebilir.

**API Base URL:** `https://anxipunk.icu`

---

## Mimari

```
┌─────────────────────┐
│ Process A:          │
│ Simulation Engine   │──┐
│ (run_simulation.py) │  │ Dosya Sistemi
└─────────────────────┘  │ (data/public/*.json)
                         │
┌─────────────────────┐  │
│ Process B:          │◄─┘
│ Read-Only API       │
│ (server.py)         │
└─────────────────────┘
         │
         ▼
   anxipunk.icu
```

- **Process A** her tick'te (`~1 saniye`) içerik üretir ve `data/public/` klasörüne JSON dosyaları yazar.
- **Process B** bu dosyaları okur ve HTTP üzerinden serve eder.
- **Tüm endpoint'ler read-only'dir** - yazma/değiştirme yapılamaz.

---

## API Endpoints

### 1. Haber Alma - `/api/news`

**Method:** `GET`

**Açıklama:** Simülasyon içinde üretilen son haber başlıklarını döner.

**Response Format:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "news_001",
      "headline": "Water Prices Surge 40% in District 7",
      "category": "economy",
      "severity": "high",
      "date": "2207-03-15",
      "tone": "dystopian",
      "visibility": "public"
    },
    {
      "id": "news_002",
      "headline": "Corporate Security Forces Deploy in Sector 4",
      "category": "political",
      "severity": "medium",
      "date": "2207-03-15",
      "tone": "neutral",
      "visibility": "public"
    }
  ],
  "count": 2
}
```

**Field Açıklamaları:**
- `id`: Benzersiz haber kimliği
- `headline`: Haber başlığı (string, max 200 karakter)
- `category`: Kategori (`economy`, `political`, `social`, `tech`, `crisis`)
- `severity`: Önem seviyesi (`low`, `medium`, `high`, `critical`)
- `date`: Simülasyon tarihi (ISO 8601 format)
- `tone`: Yazım tonu (`dystopian`, `neutral`, `optimistic`)
- `visibility`: Görünürlük (`public`, `restricted`)

**Örnek Kullanım (JavaScript):**
```javascript
fetch('https://anxipunk.icu/api/news')
  .then(res => res.json())
  .then(data => {
    data.data.forEach(news => {
      console.log(`${news.headline} - ${news.date}`);
    });
  });
```

---

### 2. Sosyal Medya Postları - `/api/social`

**Method:** `GET`

**Açıklama:** Simülasyondaki yapay kullanıcıların sosyal medya postlarını döner.

**Response Format:**
```json
{
  "status": "success",
  "data": [
    {
      "id": "post_12345",
      "user_id": "user_789",
      "username": "citizen_0789",
      "content": "Can't believe water costs more than my rent now. This city is broken.",
      "category": "daily_life",
      "sentiment": "negative",
      "engagement": {
        "likes": 45,
        "reposts": 12,
        "comments": 7
      },
      "timestamp": "2207-03-15T14:23:11Z"
    },
    {
      "id": "post_12346",
      "user_id": "user_203",
      "username": "anon_0203",
      "content": "New surveillance drones spotted in District 3. Anyone else seeing this?",
      "category": "political",
      "sentiment": "concerned",
      "engagement": {
        "likes": 128,
        "reposts": 56,
        "comments": 34
      },
      "timestamp": "2207-03-15T15:41:02Z"
    }
  ],
  "count": 2
}
```

**Field Açıklamaları:**
- `id`: Benzersiz post kimliği
- `user_id`: Kullanıcı kimliği (AI tarafından üretilmiş)
- `username`: Kullanıcı adı (anon_XXXX formatında)
- `content`: Post içeriği (string, max 280 karakter)
- `category`: Post kategorisi (`personal`, `meme`, `daily_life`, `tech`, `corporate`, `political`, `conspiracy`)
- `sentiment`: Duygu analizi (`positive`, `neutral`, `negative`, `concerned`, `angry`)
- `engagement`: Etkileşim verileri (algoritmik olarak hesaplanmış)
- `timestamp`: Post zamanı (ISO 8601)

**Örnek Kullanım (React):**
```jsx
const [posts, setPosts] = useState([]);

useEffect(() => {
  fetch('https://anxipunk.icu/api/social')
    .then(res => res.json())
    .then(data => setPosts(data.data));
}, []);

return (
  <div className="feed">
    {posts.map(post => (
      <div key={post.id} className="post">
        <h4>@{post.username}</h4>
        <p>{post.content}</p>
        <span>{post.engagement.likes} likes</span>
      </div>
    ))}
  </div>
);
```

---

### 3. Dünya Metrikleri - `/api/metrics`

**Method:** `GET`

**Açıklama:** Evrenin mevcut durumunu gösteren temel metrikleri döner.

**Response Format:**
```json
{
  "status": "success",
  "data": {
    "public_unrest": 0.67,
    "media_trust": 0.32,
    "corporate_power": 0.78,
    "state_control": 0.54,
    "surveillance_index": 0.71,
    "top_faction": "Corporate"
  },
  "timestamp": "2207-03-15T16:00:00Z"
}
```

**Field Açıklamaları:**
- `public_unrest`: Halk huzursuzluğu (0.0 - 1.0)
- `media_trust`: Medyaya güven (0.0 - 1.0)
- `corporate_power`: Kurumsal güç indeksi (0.0 - 1.0)
- `state_control`: Devlet kontrolü (0.0 - 1.0)
- `surveillance_index`: Gözetim yoğunluğu (0.0 - 1.0)
- `top_faction`: Baskın güç (`Corporate`, `State`, `Civic`, `None`)

**Kullanım Senaryosu:**
- Dashboard widget'ları
- Haber sitesinde "Dünyanın Durumu" bölümü
- Grafik ve visualizasyonlar

**Örnek (Dashboard Card):**
```jsx
const MetricCard = () => {
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    fetch('https://anxipunk.icu/api/metrics')
      .then(res => res.json())
      .then(data => setMetrics(data.data));
  }, []);

  if (!metrics) return <div>Loading...</div>;

  return (
    <div className="metrics-grid">
      <div className="metric">
        <span>Public Unrest</span>
        <progress value={metrics.public_unrest} max="1" />
        <span>{Math.round(metrics.public_unrest * 100)}%</span>
      </div>
      <div className="metric">
        <span>Media Trust</span>
        <progress value={metrics.media_trust} max="1" />
        <span>{Math.round(metrics.media_trust * 100)}%</span>
      </div>
    </div>
  );
};
```

---

### 4. Dünya Snapshot - `/api/world_snapshot`

**Method:** `GET`

**Açıklama:** Evrenin detaylı anlık görüntüsünü döner (metrics + tick + tarih).

**Response Format:**
```json
{
  "status": "success",
  "data": {
    "tick": 12847,
    "date": "2207-03-15",
    "metrics": {
      "public_unrest": 0.67,
      "media_trust": 0.32,
      "corporate_power": 0.78,
      "state_control": 0.54,
      "surveillance_index": 0.71
    },
    "status": "running"
  }
}
```

**Field Açıklamaları:**
- `tick`: Simülasyon tick sayısı (başlangıçtan itibaren)
- `date`: Simülasyon içi tarih
- `metrics`: Mevcut metrikler (aynı `/api/metrics` ile)
- `status`: Simülasyon durumu (`running`, `paused`, `error`)

---

## Rate Limiting

**Mevcut Durum:** Yok

**Öneri:** Production'da saatte 1000 request/IP limiti uygulanabilir (gelecek versiyon).

---

## CORS Ayarları

API, tüm origin'lere açıktır:
```
Access-Control-Allow-Origin: *
```

Frontend uygulamanızda CORS sorunu yaşanmaz.

---

## Error Handling

Tüm endpoint'ler aşağıdaki hata formatını döner:

```json
{
  "status": "error",
  "message": "Simulation not ready",
  "code": 503
}
```

**Olası Hata Kodları:**
- `503 Service Unavailable`: Simülasyon henüz başlatılmamış veya data dosyaları mevcut değil
- `500 Internal Server Error`: Sunucu hatası
- `404 Not Found`: Endpoint bulunamadı

---

## Frontend Entegrasyon Önerileri

### Haber Sitesi

**Önerilen Teknoloji:**
- Next.js (SEO için SSR)
- TailwindCSS (stil)
- React Query (data fetching)

**Sayfa Yapısı:**
```
/                 → Anasayfa (son haberler)
/news/[id]        → Haber detay sayfası
/metrics          → Dünya durumu dashboard
/social           → Sosyal medya akışı (opsiyonel)
```

**Örnek Anasayfa Kodu:**
```jsx
// pages/index.js
import { useState, useEffect } from 'react';

export default function Home() {
  const [news, setNews] = useState([]);
  const [metrics, setMetrics] = useState(null);

  useEffect(() => {
    // Haber çek
    fetch('https://anxipunk.icu/api/news')
      .then(res => res.json())
      .then(data => setNews(data.data));

    // Metrikler çek
    fetch('https://anxipunk.icu/api/metrics')
      .then(res => res.json())
      .then(data => setMetrics(data.data));
  }, []);

  return (
    <div className="container">
      <header>
        <h1>ChronoNet News</h1>
        <div className="metrics-bar">
          {metrics && (
            <>
              <span>Unrest: {Math.round(metrics.public_unrest * 100)}%</span>
              <span>Trust: {Math.round(metrics.media_trust * 100)}%</span>
            </>
          )}
        </div>
      </header>

      <main>
        {news.map(article => (
          <article key={article.id} className="news-card">
            <h2>{article.headline}</h2>
            <div className="meta">
              <span className="category">{article.category}</span>
              <span className="date">{article.date}</span>
            </div>
          </article>
        ))}
      </main>
    </div>
  );
}
```

### Sosyal Medya Sitesi

**Önerilen Teknoloji:**
- React (SPA yeterli)
- Infinite scroll (react-infinite-scroll-component)
- WebSocket (gelecek feature için - real-time updates)

**Sayfa Yapısı:**
```
/                 → Ana feed
/post/[id]        → Post detay + yorumlar
/user/[id]        → Kullanıcı profili (opsiyonel simülasyon verisi)
/trending         → Trend'deki konular/postlar
```

**Örnek Feed Kodu:**
```jsx
// components/Feed.js
import { useState, useEffect } from 'react';

export default function Feed() {
  const [posts, setPosts] = useState([]);

  useEffect(() => {
    const fetchPosts = async () => {
      const res = await fetch('https://anxipunk.icu/api/social');
      const data = await res.json();
      setPosts(data.data);
    };

    fetchPosts();
    
    // Her 10 saniyede bir yenile
    const interval = setInterval(fetchPosts, 10000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="feed">
      {posts.map(post => (
        <div key={post.id} className="post-card">
          <div className="user-info">
            <span className="username">@{post.username}</span>
          </div>
          <p className="content">{post.content}</p>
          <div className="engagement">
            <span>❤️ {post.engagement.likes}</span>
            <span>🔁 {post.engagement.reposts}</span>
            <span>💬 {post.engagement.comments}</span>
          </div>
          <span className="category-badge">{post.category}</span>
        </div>
      ))}
    </div>
  );
}
```

---

## Polling vs WebSocket

**Mevcut Durum:** REST API (Polling gerekli)

**Önerilen Polling Interval:**
- **Haber sitesi:** 30 saniye
- **Sosyal medya feed:** 5-10 saniye
- **Metrikler widget:** 15 saniye

**Gelecek (Phase 2):** WebSocket desteği eklendiğinde real-time push yapılabilir.

---

## Veri Güncelleme Sıklığı

- **Simülasyon Tick:** ~1 saniye
- **Data dosyası güncellemesi:** Her tick (~1 saniye)
- **Yeni haber üretimi:** Değişken (olaylara bağlı, ortalama 10-30 saniyede bir)
- **Yeni sosyal post üretimi:** Her tick'te 0-5 post arasında

---

## Cache Stratejisi

Frontend tarafında cache kullanırsanız:
- `max-age=10` (10 saniye cache)
- `stale-while-revalidate=30` (eski veri gösterirken arka planda güncelle)

**Örnek (Next.js):**
```jsx
export async function getServerSideProps() {
  const res = await fetch('https://anxipunk.icu/api/news', {
    headers: {
      'Cache-Control': 'max-age=10, stale-while-revalidate=30'
    }
  });
  const data = await res.json();

  return {
    props: { news: data.data }
  };
}
```

---

## Örnek Proje Yapısı (Next.js Haber Sitesi)

```
/my-news-site
├── pages/
│   ├── index.js                  # Anasayfa (haber listesi)
│   ├── news/[id].js              # Haber detay (şimdilik statik)
│   ├── metrics.js                # Dünya durumu dashboard
│   └── api/
│       └── proxy.js              # API proxy (opsiyonel)
├── components/
│   ├── NewsCard.js               # Haber kartı component
│   ├── MetricsWidget.js          # Metrikler gösterimi
│   └── Layout.js                 # Ana layout (header/footer)
├── lib/
│   └── api.js                    # API helper fonksiyonları
├── styles/
│   └── globals.css               # TailwindCSS import
└── package.json
```

**lib/api.js Örneği:**
```javascript
const API_BASE = 'https://anxipunk.icu/api';

export async function getNews() {
  const res = await fetch(`${API_BASE}/news`);
  if (!res.ok) throw new Error('Failed to fetch news');
  const data = await res.json();
  return data.data;
}

export async function getSocialFeed() {
  const res = await fetch(`${API_BASE}/social`);
  if (!res.ok) throw new Error('Failed to fetch social');
  const data = await res.json();
  return data.data;
}

export async function getMetrics() {
  const res = await fetch(`${API_BASE}/metrics`);
  if (!res.ok) throw new Error('Failed to fetch metrics');
  const data = await res.json();
  return data.data;
}
```

---

## Testing

**API Endpoint Test (cURL):**
```bash
# Haber testi
curl https://anxipunk.icu/api/news

# Sosyal medya testi
curl https://anxipunk.icu/api/social

# Metrikler testi
curl https://anxipunk.icu/api/metrics

# Snapshot testi
curl https://anxipunk.icu/api/world_snapshot
```

**Frontend Test:**
1. Tarayıcı console'da:
```javascript
fetch('https://anxipunk.icu/api/news')
  .then(r => r.json())
  .then(console.log);
```

2. Network tab'inde response'ları inceleyin
3. Endpoint'lerin 200 OK döndüğünü doğrulayın

---

## Gelecek Özellikler (Phase 2)

- ✅ **WebSocket Support:** Real-time push notifications
- ✅ **Filtering:** `/api/news?category=political&severity=high`
- ✅ **Pagination:** `/api/social?page=2&limit=20`
- ✅ **Search:** `/api/news?q=water`
- ✅ **Historical Data:** `/api/news/history?start_date=2207-03-01`

---

## Destek & İletişim

- **API Status:** https://anxipunk.icu/health (gelecek feature)
- **Swagger UI:** https://anxipunk.icu/docs
- **GitHub:** https://github.com/losing911/universe2200

---

## Lisans

Bu API, Universe 2200 simülasyon motoru tarafından üretilmektedir ve kişisel/ticari projelerde kullanılabilir.
