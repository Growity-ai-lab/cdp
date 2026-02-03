# CDP Mimarisi

## Genel Bakış

```
┌─────────────────────────────────────────────────────────────────┐
│                        CDP DEMO                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │   Website   │    │   Mobile    │    │    POS      │        │
│   │   Events    │    │    App      │    │   Data      │        │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘        │
│          │                  │                  │                │
│          └──────────────────┼──────────────────┘                │
│                             │                                    │
│                             ▼                                    │
│              ┌──────────────────────────┐                       │
│              │     DATA COLLECTION      │                       │
│              │   (generate_mock_data)   │                       │
│              └────────────┬─────────────┘                       │
│                           │                                      │
│                           ▼                                      │
│              ┌──────────────────────────┐                       │
│              │      DATA STORAGE        │                       │
│              │    (JSON/CSV files)      │                       │
│              │  customers, transactions │                       │
│              │        events            │                       │
│              └────────────┬─────────────┘                       │
│                           │                                      │
│                           ▼                                      │
│              ┌──────────────────────────┐                       │
│              │    SEGMENT ENGINE        │                       │
│              │   (segment_engine.py)    │                       │
│              │  - Profile conditions    │                       │
│              │  - Transaction rules     │                       │
│              │  - Event conditions      │                       │
│              └────────────┬─────────────┘                       │
│                           │                                      │
│                           ▼                                      │
│              ┌──────────────────────────┐                       │
│              │    PLATFORM EXPORT       │                       │
│              │  (platform_export.py)    │                       │
│              │  - SHA256 hashing        │                       │
│              │  - Format conversion     │                       │
│              └────────────┬─────────────┘                       │
│                           │                                      │
│          ┌────────────────┼────────────────┐                    │
│          ▼                ▼                ▼                    │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │    Meta     │  │   Google    │  │   TikTok    │            │
│   │  Audiences  │  │   Ads API   │  │  Audiences  │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Modüller

### 1. generate_mock_data.py
**Amaç:** Demo için gerçekçi test verisi oluşturma

**Veri Modelleri:**
- `Customer`: Profil, tercihler, opt-in durumu
- `Transaction`: Satın alma, yakıt, market
- `Event`: Dijital etkileşimler

**Çıktı:**
- `data/customers.json`
- `data/transactions.json`
- `data/events.json`

### 2. segment_engine.py
**Amaç:** Müşteri segmentasyonu

**Bileşenler:**
- `SegmentDefinition`: Segment tanımı (isim, koşullar, mantık)
- `SegmentEngine`: Koşul değerlendirme motoru

**Koşul Tipleri:**
- Profil koşulları (city, age, segment)
- İşlem koşulları (tx_count, tx_total_amount)
- Event koşulları (event_count)

### 3. platform_export.py
**Amaç:** Segmentleri reklam platformlarına export

**İşlemler:**
- PII normalizasyonu
- SHA256 hashing
- Platform-specific CSV formatı

## Veri Akışı

```
1. Veri Toplama
   Raw data → JSON files

2. Indexleme
   customers.json → customer_map (dict)
   transactions.json → customer_transactions (customer_id → list)
   events.json → customer_events (customer_id → list)

3. Segment Çalıştırma
   SegmentDefinition → SegmentEngine.run_segment() → List[Customer]

4. Export
   List[Customer] → hash + format → CSV file
```

## Gelecek Mimari (v1.0)

```
┌─────────────────────────────────────────────────────────────────┐
│                      PRODUCTION CDP                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│   ┌─────────────┐    ┌─────────────┐    ┌─────────────┐        │
│   │  GTM/SDK    │    │   Webhook   │    │   Batch     │        │
│   │   Events    │    │   Receiver  │    │   Upload    │        │
│   └──────┬──────┘    └──────┬──────┘    └──────┬──────┘        │
│          │                  │                  │                │
│          └──────────────────┼──────────────────┘                │
│                             │                                    │
│                             ▼                                    │
│              ┌──────────────────────────┐                       │
│              │       EVENT STREAM       │                       │
│              │   (Kafka / Pub/Sub)      │                       │
│              └────────────┬─────────────┘                       │
│                           │                                      │
│                           ▼                                      │
│              ┌──────────────────────────┐                       │
│              │      DATA WAREHOUSE      │                       │
│              │   (BigQuery / Snowflake) │                       │
│              │                          │                       │
│              │  ┌────────┐ ┌────────┐  │                       │
│              │  │ Bronze │→│ Silver │  │                       │
│              │  │  Raw   │ │ Clean  │  │                       │
│              │  └────────┘ └───┬────┘  │                       │
│              │                 │        │                       │
│              │                 ▼        │                       │
│              │           ┌────────┐     │                       │
│              │           │  Gold  │     │                       │
│              │           │Profiles│     │                       │
│              │           └────────┘     │                       │
│              └────────────┬─────────────┘                       │
│                           │                                      │
│                           ▼                                      │
│              ┌──────────────────────────┐                       │
│              │      REVERSE ETL         │                       │
│              │   (Hightouch / Census)   │                       │
│              └────────────┬─────────────┘                       │
│                           │                                      │
│          ┌────────────────┼────────────────┐                    │
│          ▼                ▼                ▼                    │
│   ┌─────────────┐  ┌─────────────┐  ┌─────────────┐            │
│   │  Meta CAPI  │  │ Google Ads  │  │TikTok Events│            │
│   │    Auto     │  │   Auto      │  │    Auto     │            │
│   └─────────────┘  └─────────────┘  └─────────────┘            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Teknoloji Seçenekleri

### Veri Toplama
- **Demo:** Python script
- **Prod:** RudderStack, Segment, GTM Server-side

### Veri Depolama
- **Demo:** JSON/CSV files
- **Prod:** BigQuery, Snowflake, Databricks

### Reverse ETL
- **Demo:** Manuel CSV export
- **Prod:** Hightouch, Census, Rudderstack Profiles

### Orchestration
- **Demo:** CLI
- **Prod:** Airflow, Prefect, Dagster
