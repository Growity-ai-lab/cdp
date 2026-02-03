# Platform Export Rehberi

CDP'den reklam platformlarına audience export etme rehberi.

## Genel Bilgiler

### Hash Formatı
Tüm PII (email, telefon) verileri **SHA256** ile hash'lenerek export edilir.

```python
# Örnek hash
email = "ornek@gmail.com"
hash = "a1b2c3d4..."  # 64 karakter SHA256
```

### Normalizasyon
- Email: Küçük harf, trim
- Telefon: Sadece rakamlar, +90 ile başlar

---

## Meta (Facebook/Instagram)

### Export Komutu
```bash
python main.py export premium_fuel_lovers
# Çıktı: exports/meta_audience_premium_fuel_lovers_YYYYMMDD.csv
```

### Dosya Formatı
```csv
email,phone
a1b2c3d4e5f6...,9a8b7c6d5e4f...
```

### Yükleme Adımları
1. [Business Manager](https://business.facebook.com) > Audiences
2. Create Audience > Custom Audience
3. Customer List seç
4. "Upload a file" seç
5. CSV dosyasını yükle
6. **"Customer data is hashed"** seçeneğini işaretle ✓
7. Mapping'i kontrol et (email → Email, phone → Phone)
8. Create Audience

### Lookalike Oluşturma
Custom Audience oluşturduktan sonra:
1. Audience'a tıkla > ... > Create Lookalike
2. Ülke: Türkiye
3. Audience size: %1-3 (dar) veya %3-5 (geniş)

---

## Google Ads

### Export Komutu
```bash
python main.py export premium_fuel_lovers
# Çıktı: exports/google_audience_premium_fuel_lovers_YYYYMMDD.csv
```

### Dosya Formatı
```csv
Email,Phone,Country
a1b2c3d4e5f6...,9a8b7c6d5e4f...,TR
```

### Yükleme Adımları
1. [Google Ads](https://ads.google.com) > Tools & Settings
2. Audience Manager > Customer Lists
3. \+ butonu > Upload customer list
4. CSV dosyasını yükle
5. "Hashed data" seçeneğini işaretle
6. Listeye isim ver
7. Upload and create list

### Minimum Gereksinim
- En az 1000 eşleşen kullanıcı gerekli
- Daha az kullanıcı varsa liste kullanılamaz

---

## TikTok Ads

### Export Komutu
```bash
python main.py export premium_fuel_lovers
# Çıktı: exports/tiktok_audience_premium_fuel_lovers_YYYYMMDD.csv
```

### Dosya Formatı
```csv
EMAIL_SHA256,PHONE_SHA256
a1b2c3d4e5f6...,9a8b7c6d5e4f...
```

### Yükleme Adımları
1. [TikTok Ads Manager](https://ads.tiktok.com)
2. Assets > Audiences
3. Create Audience > Customer File
4. File Type: Customer file with hashed data
5. CSV dosyasını yükle
6. Identifier'ları seç (SHA256_EMAIL, SHA256_PHONE)
7. Confirm

---

## Otomatik Sync (Gelecek)

### Hightouch Entegrasyonu
```
CDP (BigQuery) → Hightouch → Meta/Google/TikTok
```

### Önerilen Sync Frekansı
| Segment Tipi | Frekans |
|--------------|---------|
| Churn Risk | Günlük |
| High Value | Haftalık |
| Campaign-specific | İhtiyaca göre |

---

## Troubleshooting

### "Match rate çok düşük"
- Email normalizasyonu kontrol et (lowercase)
- Telefon formatı kontrol et (+90 ile başlamalı)
- Gerçek email mi kontrol et (fake generator değil)

### "Audience kullanılamıyor"
- Minimum kullanıcı sayısı kontrolü (Google: 1000)
- Hash algoritması doğru mu (SHA256)
- Dosya encoding UTF-8 mi

### "Upload başarısız"
- Dosya boyutu limiti (genelde 1GB)
- Satır sayısı limiti
- CSV format hatası (virgül yerine noktalı virgül)
