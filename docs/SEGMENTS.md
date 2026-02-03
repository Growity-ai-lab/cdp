# Segment Tanımları

Bu dokümanda CDP'de kullanılan hazır segmentler açıklanmaktadır.

## Hazır Segmentler

### 1. Premium Yakıt Severler (`premium_fuel_lovers`)
- **Tanım:** Son 90 günde 3+ kez premium yakıt alan
- **Kullanım:** Premium ürün lansmanları, yüksek marjlı cross-sell

### 2. Yüksek Değerli Müşteriler (`high_value_customers`)
- **Tanım:** Son 90 günde 5000 TL+ harcama
- **Kullanım:** VIP kampanyalar, retention

### 3. Aktif App Kullanıcıları (`app_active_users`)
- **Tanım:** App'i olan ve son 30 günde 5+ event üreten
- **Kullanım:** App-only kampanyalar, push notification

### 4. Churn Riski (`churn_risk`)
- **Tanım:** Eskiden düzenli gelip son 60 günde gelmeyen
- **Kullanım:** Win-back kampanyaları

### 5. İstanbul Premium (`istanbul_premium`)
- **Tanım:** İstanbul'da yaşayan premium segment
- **Kullanım:** Bölgesel kampanyalar

### 6. Market Alışverişçileri (`market_shoppers`)
- **Tanım:** Son 30 günde 3+ market alışverişi
- **Kullanım:** Cross-sell, combo teklifler

### 7. Email ile Ulaşılabilir (`email_reachable`)
- **Tanım:** Email opt-in vermiş premium müşteriler
- **Kullanım:** Email marketing

## Yeni Segment Oluşturma

```python
from src.segment_engine import SegmentDefinition

my_segment = SegmentDefinition(
    name="Segment Adı",
    description="Açıklama",
    conditions=[
        {"field": "city", "operator": "==", "value": "İstanbul"},
        {"field": "tx_total_amount", "operator": ">=", "value": 10000, "days": 90},
    ],
    logic="AND"
)
```

## Koşul Alanları

### Profil
- `city`, `district`, `age`, `gender`
- `segment` (premium/regular/occasional)
- `has_app`, `email_opted_in`, `sms_opted_in`, `loyalty_card`

### İşlem (tx_)
- `tx_count` - İşlem sayısı
- `tx_total_amount` - Toplam harcama
- `tx_avg_amount` - Ortalama işlem
- `tx_last_days` - Son işlemden bu yana gün

### Event (event_)
- `event_count` - Event sayısı

## Operatörler
- `==`, `!=` - Eşit / eşit değil
- `>`, `>=`, `<`, `<=` - Karşılaştırma
- `in` - Liste içinde
- `contains` - String içeriyor
