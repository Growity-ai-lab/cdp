# CDP - Customer Data Platform Demo

Time & Growity için geliştirilmiş basit CDP proof-of-concept sistemi.

## 🎯 Amaç

Bu proje, CDP'nin temel işlevlerini göstermek için oluşturulmuş bir demo sistemdir:
- Müşteri verilerini birleştirme
- Davranışsal segmentasyon
- Reklam platformlarına audience export (Meta, Google, TikTok)

## 🚀 Hızlı Başlangıç

```bash
# Repo'yu klonla
git clone https://github.com/Growity-ai-lab/cdp.git
cd cdp

# (Opsiyonel) Virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Bağımlılıkları yükle
pip install -r requirements.txt

# Demo'yu çalıştır
python main.py demo
```

## 📋 Komutlar

```bash
python main.py generate    # Mock veri oluştur (1000 müşteri, 90 günlük işlem)
python main.py segments    # Tüm segmentleri listele ve analiz et
python main.py export      # Tüm segmentleri platformlara export et
python main.py export premium_fuel_lovers  # Tek segment export
python main.py demo        # Interaktif tam demo
python main.py help        # Yardım
```

## 📁 Proje Yapısı

```
cdp/
├── main.py                     # Ana CLI uygulaması
├── app.py                      # Streamlit dashboard
├── requirements.txt            # Python bağımlılıkları
├── src/
│   ├── __init__.py
│   ├── generate_mock_data.py   # Mock veri oluşturucu
│   ├── segment_engine.py       # Segmentasyon motoru
│   └── platform_export.py      # Platform export modülü
├── pages/                      # Streamlit sayfaları
│   ├── 1_Müşteri_Analizi.py   # Müşteri analizi sayfası
│   ├── 2_Segment_Builder.py   # Segment builder sayfası
│   └── 3_Export.py            # Export sayfası
├── data/                       # Oluşturulan veriler (gitignore)
├── exports/                    # Export dosyaları (gitignore)
├── docs/
│   ├── SEGMENTS.md            # Segment tanımları
│   ├── EXPORT_GUIDE.md        # Platform export rehberi
│   └── ARCHITECTURE.md        # Mimari dokümantasyon
└── tests/                      # (TODO) Unit testler
```

## 🎯 Hazır Segmentler

| Segment Key | Açıklama | Örnek Kullanım |
|-------------|----------|----------------|
| `premium_fuel_lovers` | Son 90 günde 3+ kez premium yakıt alan | Yeni premium ürün lansmanı |
| `high_value_customers` | Son 90 günde 5000 TL+ harcama | VIP kampanyalar |
| `app_active_users` | App'i olan ve aktif kullanan | App-only promosyonlar |
| `churn_risk` | Eskiden düzenli gelip artık gelmeyen | Win-back kampanyaları |
| `istanbul_premium` | İstanbul'daki premium müşteriler | Bölgesel kampanyalar |
| `market_shoppers` | Market alışverişi yapanlar | Cross-sell kampanyaları |
| `email_reachable` | Email opt-in vermiş premium | Email marketing |

## 📤 Platform Export

### Meta (Facebook/Instagram)
```bash
python main.py export premium_fuel_lovers
# Çıktı: exports/meta_audience_premium_fuel_lovers_YYYYMMDD.csv
```

**Yükleme:**
1. Business Manager > Audiences > Create Audience > Custom Audience
2. Customer List seç
3. CSV dosyasını yükle
4. "Data is hashed" seçeneğini işaretle

### Google Ads
```bash
python main.py export premium_fuel_lovers
# Çıktı: exports/google_audience_premium_fuel_lovers_YYYYMMDD.csv
```

**Yükleme:**
1. Google Ads > Tools > Audience Manager
2. + > Customer List
3. CSV dosyasını yükle

### TikTok Ads
```bash
python main.py export premium_fuel_lovers
# Çıktı: exports/tiktok_audience_premium_fuel_lovers_YYYYMMDD.csv
```

**Yükleme:**
1. TikTok Ads Manager > Assets > Audiences
2. Create Audience > Customer File
3. CSV dosyasını yükle

## 🔧 Kendi Segmentinizi Tanımlama

```python
from src.segment_engine import SegmentEngine, SegmentDefinition

engine = SegmentEngine("data")

# Yeni segment tanımla
my_segment = SegmentDefinition(
    name="İstanbul Yüksek Değerli App Kullanıcıları",
    description="İstanbul'da yaşayan, 10K+ harcama yapan, app kullanan müşteriler",
    conditions=[
        {"field": "city", "operator": "==", "value": "İstanbul"},
        {"field": "tx_total_amount", "operator": ">=", "value": 10000, "days": 90},
        {"field": "has_app", "operator": "==", "value": True},
    ],
    logic="AND"  # Tüm koşullar sağlanmalı
)

# Çalıştır
results = engine.run_segment(my_segment)
stats = engine.get_segment_stats(results)

print(f"Eşleşen: {stats['count']} müşteri")
print(f"Toplam gelir: {stats['total_revenue']:,.0f} TL")
```

## 📊 Kullanılabilir Koşul Alanları

### Profil Alanları
| Alan | Tip | Açıklama |
|------|-----|----------|
| `city` | string | Şehir adı |
| `district` | string | İlçe adı |
| `age` | int | Yaş |
| `gender` | string | M/F |
| `segment` | string | premium/regular/occasional |
| `has_app` | bool | App kullanıcısı mı |
| `email_opted_in` | bool | Email izni var mı |
| `sms_opted_in` | bool | SMS izni var mı |
| `loyalty_card` | bool | Sadakat kartı var mı |

### İşlem Alanları (tx_)
| Alan | Tip | Açıklama |
|------|-----|----------|
| `tx_count` | int | İşlem sayısı |
| `tx_total_amount` | float | Toplam harcama |
| `tx_avg_amount` | float | Ortalama işlem tutarı |
| `tx_last_days` | int | Son işlemden bu yana geçen gün |

### Event Alanları (event_)
| Alan | Tip | Açıklama |
|------|-----|----------|
| `event_count` | int | Event sayısı |

### Operatörler
- `==`, `eq`: Eşit
- `!=`, `ne`: Eşit değil
- `>`, `gt`: Büyük
- `>=`, `gte`: Büyük eşit
- `<`, `lt`: Küçük
- `<=`, `lte`: Küçük eşit
- `in`: Liste içinde
- `contains`: İçeriyor (string)

## 🛡️ KVKK/GDPR Uyumu

- ✅ Tüm PII verisi SHA256 ile hash'lenerek export edilir
- ✅ Opt-out durumu (`email_opted_in`, `sms_opted_in`) kontrol edilebilir
- ✅ Ham veri hiçbir platforma gönderilmez
- ✅ Audit trail için export raporları oluşturulur

## 🖥️ Dashboard (v0.4)

Streamlit tabanlı görsel arayüz ile CDP'yi kullanın:

```bash
# Dashboard'u başlat
streamlit run app.py
```

**Sayfalar:**
- 📊 **Ana Sayfa** - KPI'lar, genel bakış, günlük trendler
- 👥 **Müşteri Analizi** - Demografik dağılım, RFM analizi, filtreler
- 🎯 **Segment Builder** - Hazır segmentler, özel segment oluşturma, karşılaştırma
- 📤 **Export** - Platform export, toplu export, geçmiş yönetimi

## 🔜 Yol Haritası

### v0.2 - API Entegrasyonu
- [ ] Meta Conversions API otomatik upload
- [ ] Google Ads API otomatik upload
- [ ] TikTok Events API otomatik upload

### v0.3 - Gerçek Zamanlı
- [ ] Webhook endpoint ile event toplama
- [ ] Real-time segment güncelleme
- [ ] Incremental sync

### v0.4 - Dashboard ✅
- [x] Streamlit görsel arayüz
- [x] Segment builder UI
- [x] Analytics dashboard

### v1.0 - Production
- [ ] PostgreSQL/BigQuery desteği
- [ ] Multi-tenant mimari
- [ ] Rıza yönetimi (consent management)
- [ ] Scheduling (Airflow/Prefect)

## 🤝 Katkıda Bulunma

1. Fork'la
2. Feature branch oluştur (`git checkout -b feature/amazing-feature`)
3. Commit'le (`git commit -m 'Add amazing feature'`)
4. Push'la (`git push origin feature/amazing-feature`)
5. Pull Request aç

## 📝 Lisans

Bu proje Time & Growity'ye aittir. Dahili kullanım içindir.

---

**Sorular?** Slack: #cdp-dev
