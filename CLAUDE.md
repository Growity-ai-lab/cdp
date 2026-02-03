# CLAUDE.md - CDP Project Context

Bu dosya Claude Code'un projeyi anlaması için context sağlar.

## Proje Özeti

**CDP Demo** - Time & Growity medya ajansı için geliştirilmiş basit Customer Data Platform.

**Amaç:** 
- Müşteri verilerini birleştirmek
- Davranışsal segmentasyon yapmak
- Meta/Google/TikTok'a audience export etmek

## Teknoloji Stack

- **Dil:** Python 3.9+
- **Veri:** JSON/CSV (demo için)
- **Hash:** SHA256 (PII için)
- **CLI:** argparse
- **Prod hedef:** BigQuery + Hightouch

## Proje Yapısı

```
cdp/
├── main.py                 # CLI entry point
├── src/
│   ├── __init__.py
│   ├── generate_mock_data.py   # Mock veri oluşturucu
│   ├── segment_engine.py       # Segmentasyon motoru
│   └── platform_export.py      # Meta/Google/TikTok export
├── data/                   # Oluşturulan veriler (gitignore)
├── exports/                # Export dosyaları (gitignore)
└── docs/                   # Dokümantasyon
```

## Önemli Komutlar

```bash
python main.py generate    # 1000 müşteri, 15K işlem oluştur
python main.py segments    # Segmentleri analiz et
python main.py export      # Platformlara export et
python main.py demo        # Tam demo
```

## Veri Modeli

### Customer
```python
{
    "customer_id": "PO100001",
    "email": "ahmet.yilmaz@gmail.com",
    "phone": "+905301234567",
    "city": "İstanbul",
    "segment": "premium",  # premium/regular/occasional
    "has_app": True,
    "email_opted_in": True,
    "email_hash": "sha256...",
    "phone_hash": "sha256..."
}
```

### Transaction
```python
{
    "transaction_id": "TX12345678",
    "customer_id": "PO100001",
    "timestamp": "2024-01-15 14:30:00",
    "fuel_type": "Premium Dizel",
    "fuel_amount": 1250.50,
    "is_premium_fuel": True,
    "market_amount": 85.00,
    "total_amount": 1335.50
}
```

### Event
```python
{
    "event_id": "EV12345678",
    "customer_id": "PO100001",
    "timestamp": "2024-01-15 10:00:00",
    "event_type": "app_open",
    "platform": "app"
}
```

## Segment Tanımlama

```python
SegmentDefinition(
    name="Premium Yakıt Severler",
    description="Son 90 günde 3+ premium yakıt alan",
    conditions=[
        {
            "field": "tx_count",
            "operator": ">=",
            "value": 3,
            "days": 90,
            "filter": {"field": "is_premium_fuel", "value": True}
        }
    ],
    logic="AND"
)
```

## Geliştirme Öncelikleri

1. **v0.2 - API Entegrasyonu**
   - Meta Conversions API
   - Google Ads API
   - Otomatik audience sync

2. **v0.3 - Real-time**
   - Webhook endpoint
   - Event streaming
   - Incremental sync

3. **v0.4 - Dashboard**
   - Streamlit UI
   - Segment builder
   - Analytics

## Dikkat Edilmesi Gerekenler

- PII her zaman hash'lenmeli (SHA256)
- Email lowercase + trim normalize edilmeli
- Telefon +90XXXXXXXXXX formatında olmalı
- KVKK için opt-in kontrol edilmeli
- Export dosyaları gitignore'da (hassas veri)

## Test Verisi

Mock data Petrol Ofisi senaryosunu simüle eder:
- Yakıt satışları (normal + premium)
- Market alışverişleri
- App kullanımı
- Sadakat kartı

## Mevcut Müşteriler (Gerçek Dünya)

T&G müşterileri için CDP kullanım senaryoları:
- **Petrol Ofisi:** POS + dijital entegrasyon
- **Uludağ İçecek:** Sezonluk kampanya optimizasyonu
- **Hayhay BNPL:** App kullanıcı segmentasyonu
- **Joseph Mews:** Lead lifecycle tracking
- **UNICEF:** Bağışçı retention
