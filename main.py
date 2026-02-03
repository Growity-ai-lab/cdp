#!/usr/bin/env python3
"""
CDP Demo - Ana Uygulama
Basit CDP sistemi demonstrasyonu

Kullanım:
  python main.py generate    # Mock veri oluştur
  python main.py segments    # Segmentleri listele ve çalıştır
  python main.py export      # Tüm segmentleri platformlara export et
  python main.py export premium_fuel_lovers  # Tek segment export
  python main.py upload meta premium_fuel_lovers  # API ile yükle
  python main.py upload meta premium_fuel_lovers --dry-run  # Test modu
  python main.py config      # Credential durumunu kontrol et
  python main.py demo        # Tüm demo akışını çalıştır
"""

import sys
import os
from pathlib import Path

# src klasörünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent / "src"))

from generate_mock_data import generate_customers, generate_transactions, generate_digital_events, save_data
from segment_engine import SegmentEngine, PREDEFINED_SEGMENTS
from platform_export import PlatformExporter
from config import CDPConfig, setup_logging
from api_clients import MetaClient, GoogleClient, TikTokClient


def print_header(title: str):
    """Başlık yazdır"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def cmd_generate():
    """Mock veri oluştur"""
    print_header("📊 MOCK VERİ OLUŞTURUCU")
    
    print("\n🔄 Müşteri verileri oluşturuluyor...")
    customers = generate_customers(1000)
    
    print("🔄 İşlem verileri oluşturuluyor...")
    transactions = generate_transactions(customers, days=90)
    
    print("🔄 Dijital event verileri oluşturuluyor...")
    events = generate_digital_events(customers, days=90)
    
    print("💾 Veriler kaydediliyor...")
    save_data(customers, transactions, events, "data")
    
    # Özet
    print("\n✅ Veri oluşturma tamamlandı!")
    print(f"\n📈 Özet:")
    print(f"   • Müşteri: {len(customers)}")
    print(f"   • İşlem: {len(transactions)}")
    print(f"   • Event: {len(events)}")
    
    premium_count = len([c for c in customers if c["segment"] == "premium"])
    print(f"\n   • Premium müşteri: {premium_count} (%{premium_count/10:.0f})")
    print(f"   • App kullanıcı: {len([c for c in customers if c['has_app']])} (%{len([c for c in customers if c['has_app']])/10:.0f})")


def cmd_segments():
    """Segmentleri listele ve çalıştır"""
    print_header("🎯 SEGMENT ANALİZİ")
    
    # Veri var mı kontrol et
    if not Path("data/customers.json").exists():
        print("\n⚠️  Veri bulunamadı. Önce 'python main.py generate' çalıştırın.")
        return
    
    engine = SegmentEngine("data")
    
    print(f"\n📊 Yüklenen veri:")
    print(f"   • {len(engine.customers)} müşteri")
    print(f"   • {len(engine.transactions)} işlem")
    print(f"   • {len(engine.events)} event")
    
    print("\n" + "-" * 70)
    print("📋 Tanımlı Segmentler:")
    print("-" * 70)
    
    for i, (key, segment) in enumerate(PREDEFINED_SEGMENTS.items(), 1):
        results = engine.run_segment(segment)
        stats = engine.get_segment_stats(results)
        
        print(f"\n{i}. {segment.name} [{key}]")
        print(f"   📝 {segment.description}")
        print(f"   👥 Müşteri: {stats['count']} ({stats.get('percentage', 0)}%)")
        
        if stats['count'] > 0:
            print(f"   💰 Toplam Gelir: {stats.get('total_revenue', 0):,.0f} TL")
            print(f"   📱 App Kullanım: %{stats.get('has_app_pct', 0)}")
            
            # Şehir dağılımı (ilk 3)
            cities = stats.get('cities', {})
            top_cities = list(cities.items())[:3]
            if top_cities:
                city_str = ", ".join([f"{c}: {n}" for c, n in top_cities])
                print(f"   🏙️  Şehirler: {city_str}")


def cmd_export(segment_key: str = None):
    """Segmentleri platformlara export et"""
    print_header("📤 PLATFORM EXPORT")
    
    # Veri var mı kontrol et
    if not Path("data/customers.json").exists():
        print("\n⚠️  Veri bulunamadı. Önce 'python main.py generate' çalıştırın.")
        return
    
    exporter = PlatformExporter("data", "exports")
    
    if segment_key:
        # Tek segment
        if segment_key not in PREDEFINED_SEGMENTS:
            print(f"\n❌ Bilinmeyen segment: {segment_key}")
            print(f"   Mevcut segmentler: {', '.join(PREDEFINED_SEGMENTS.keys())}")
            return
        
        print(f"\n🔄 '{segment_key}' segmenti export ediliyor...")
        exports = exporter.export_segment(segment_key, ["meta", "google", "tiktok"])
        
        if exports:
            print("\n✅ Export tamamlandı:")
            for platform, filepath in exports.items():
                print(f"   • {platform}: {filepath}")
    else:
        # Tüm segmentler
        print("\n🔄 Tüm segmentler export ediliyor...")
        all_exports = exporter.export_all_segments()
        
        report = exporter.generate_summary_report(all_exports)
        print(report)
        
        print("\n✅ Tüm exportlar tamamlandı!")
        print(f"   📁 Export klasörü: exports/")


def cmd_demo():
    """Tüm demo akışını çalıştır"""
    print_header("🚀 CDP DEMO - TAM AKIŞ")
    
    print("\n" + "=" * 70)
    print("  Bu demo, basit bir CDP sisteminin nasıl çalıştığını gösterir:")
    print("  1. Mock veri oluşturma (müşteri, işlem, dijital event)")
    print("  2. Segment tanımlama ve çalıştırma")
    print("  3. Platformlara export (Meta, Google, TikTok)")
    print("=" * 70)
    
    input("\n[Enter] tuşuna basarak başlayın...")
    
    # Adım 1: Veri oluştur
    cmd_generate()
    
    input("\n[Enter] tuşuna basarak segmentasyona geçin...")
    
    # Adım 2: Segmentler
    cmd_segments()
    
    input("\n[Enter] tuşuna basarak export'a geçin...")
    
    # Adım 3: Export
    cmd_export()
    
    # Kapanış
    print_header("✅ DEMO TAMAMLANDI")
    print("""
    Bu demo ile gördükleriniz:
    
    1. 📊 VERİ TOPLAMA
       - 1000 müşteri profili (demografik, tercihler, opt-in durumu)
       - 90 günlük işlem geçmişi (yakıt, market alışverişi)
       - Dijital etkileşimler (web, app, email)
    
    2. 🎯 SEGMENTASYON
       - Davranışsal segmentler (premium yakıt severler, yüksek değerli)
       - Engagement segmentleri (aktif app kullanıcıları)
       - Risk segmentleri (churn riski)
       - Kombine segmentler (İstanbul + Premium)
    
    3. 📤 AKTİVASYON
       - Meta Custom Audiences (SHA256 hash)
       - Google Customer Match
       - TikTok Custom Audiences
       - Otomatik hash ve format dönüşümü
    
    🔜 Sonraki adımlar:
       - Meta API entegrasyonu (otomatik upload)
       - Gerçek zamanlı event toplama
       - Streamlit ile görsel arayüz
    """)


def cmd_upload(platform: str, segment_key: str, dry_run: bool = False):
    """Segment'i platforma API ile yükle"""
    print_header(f"📤 API UPLOAD - {platform.upper()}")

    # Veri var mı kontrol et
    if not Path("data/customers.json").exists():
        print("\n⚠️  Veri bulunamadı. Önce 'python main.py generate' çalıştırın.")
        return

    # Logging ayarla
    setup_logging()

    # Konfigürasyon yükle
    config = CDPConfig.load()

    # Dry run kontrolü
    if dry_run:
        print("\n🔶 DRY-RUN MODU: Gerçek upload yapılmayacak")

    # Platform kontrolü
    valid, message = config.validate_platform(platform)
    if not valid and not dry_run:
        print(f"\n⚠️  {message}")
        print("   Simülasyon modunda devam ediliyor...")

    # Segment kontrolü
    if segment_key not in PREDEFINED_SEGMENTS:
        print(f"\n❌ Bilinmeyen segment: {segment_key}")
        print(f"   Mevcut segmentler: {', '.join(PREDEFINED_SEGMENTS.keys())}")
        return

    # Engine ve segment hazırla
    engine = SegmentEngine("data")
    segment = PREDEFINED_SEGMENTS[segment_key]
    results = engine.run_segment(segment)

    if not results:
        print(f"\n⚠️  Segment '{segment.name}' boş.")
        return

    print(f"\n📊 Segment: {segment.name}")
    print(f"   Toplam müşteri: {len(results)}")

    # Exporter ile hash'le
    exporter = PlatformExporter("data", "exports")

    # Consent kontrolü ve hash'leme
    hashed_users = []
    for c in results:
        if not c.get("email_opted_in", False):
            continue  # Opt-in olmayanları atla

        user = {}
        if c.get("email"):
            user["email"] = exporter._hash_value(c["email"])
        if c.get("phone"):
            user["phone"] = exporter._hash_value(exporter._normalize_phone(c["phone"]))

        if user:
            hashed_users.append(user)

    print(f"   Export edilecek (opt-in): {len(hashed_users)}")

    if not hashed_users:
        print("\n⚠️  Yüklenecek müşteri yok (consent kontrolü).")
        return

    # Client seç
    if platform == "meta":
        client = MetaClient(config.meta, dry_run=dry_run)
    elif platform == "google":
        client = GoogleClient(config.google, dry_run=dry_run)
    elif platform == "tiktok":
        client = TikTokClient(config.tiktok, dry_run=dry_run)
    else:
        print(f"\n❌ Desteklenmeyen platform: {platform}")
        print("   Desteklenen: meta, google, tiktok")
        return

    print(f"\n🔄 {platform.upper()} API'sine yükleniyor...")

    # Upload et
    result = client.upload_segment(
        segment_name=segment_key,
        users=hashed_users,
        description=segment.description
    )

    # Sonuç
    if result.success:
        print(f"\n✅ Upload başarılı!")
        print(f"   Audience: {result.audience_name}")
        if result.audience_id:
            print(f"   ID: {result.audience_id}")
        print(f"   Yüklenen: {result.uploaded_count} kullanıcı")
        if result.dry_run:
            print("\n   ℹ️  DRY-RUN: Gerçek upload yapılmadı")
    else:
        print(f"\n❌ Upload başarısız: {result.error_message}")


def cmd_config():
    """Konfigürasyon durumunu kontrol et"""
    print_header("⚙️  KONFİGÜRASYON KONTROLÜ")

    config = CDPConfig.load()

    print("\n📋 Platform Durumları:")
    print("-" * 50)

    platforms = [
        ("Meta (Facebook/Instagram)", "meta", config.meta.is_valid()),
        ("Google Ads", "google", config.google.is_valid()),
        ("TikTok Ads", "tiktok", config.tiktok.is_valid()),
    ]

    for name, key, valid in platforms:
        status = "✅ Hazır" if valid else "❌ Eksik"
        print(f"   {status}  {name}")

    configured_count = sum(1 for _, _, v in platforms if v)

    if configured_count == 0:
        print("\n⚠️  Hiçbir platform yapılandırılmamış.")
        print("\n📝 Kurulum:")
        print("   1. .env.example dosyasını .env olarak kopyalayın:")
        print("      cp .env.example .env")
        print("   2. .env dosyasını düzenleyip credential'ları girin")
        print("   3. Tekrar 'python main.py config' çalıştırın")
    else:
        print(f"\n✅ {configured_count}/3 platform yapılandırılmış")

    print("\n💡 İpucu: --dry-run ile credential olmadan test edebilirsiniz:")
    print("   python main.py upload meta premium_fuel_lovers --dry-run")


def cmd_help():
    """Yardım mesajı"""
    print("""
CDP Demo - Customer Data Platform

Kullanım:
  python main.py <komut> [argümanlar]

Veri Komutları:
  generate              Mock veri oluştur (1000 müşteri, 90 günlük işlem)
  segments              Tüm segmentleri listele ve analiz et

Export Komutları (CSV dosyası):
  export [segment]      Segment(ler)i CSV olarak export et

Upload Komutları (API):
  upload <platform> <segment>           Segment'i API ile yükle
  upload <platform> <segment> --dry-run Test modu (upload yapmadan)

Konfigürasyon:
  config                Platform credential durumunu kontrol et

Demo:
  demo                  Interaktif demo - tüm akışı göster
  help                  Bu yardım mesajını göster

Örnekler:
  python main.py demo
  python main.py generate
  python main.py segments
  python main.py export premium_fuel_lovers
  python main.py upload meta premium_fuel_lovers
  python main.py upload google high_value_customers --dry-run
  python main.py config

Platformlar:
  meta     - Facebook/Instagram Custom Audiences
  google   - Google Ads Customer Match
  tiktok   - TikTok Custom Audiences

Segment isimleri:
  - premium_fuel_lovers   : Premium yakıt alan müşteriler
  - high_value_customers  : Yüksek harcama yapanlar
  - app_active_users      : Aktif app kullanıcıları
  - churn_risk            : Kaybetme riski olanlar
  - istanbul_premium      : İstanbul'daki premium müşteriler
  - market_shoppers       : Market alışverişi yapanlar
  - email_reachable       : Email ile ulaşılabilir premium
""")


def main():
    """Ana giriş noktası"""
    if len(sys.argv) < 2:
        cmd_help()
        return

    command = sys.argv[1].lower()

    if command == "generate":
        cmd_generate()
    elif command == "segments":
        cmd_segments()
    elif command == "export":
        segment_key = sys.argv[2] if len(sys.argv) > 2 else None
        cmd_export(segment_key)
    elif command == "upload":
        if len(sys.argv) < 4:
            print("❌ Eksik argüman!")
            print("\nKullanım: python main.py upload <platform> <segment> [--dry-run]")
            print("Örnek:    python main.py upload meta premium_fuel_lovers")
            print("          python main.py upload google high_value_customers --dry-run")
            return
        platform = sys.argv[2].lower()
        segment_key = sys.argv[3]
        dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
        cmd_upload(platform, segment_key, dry_run)
    elif command == "config":
        cmd_config()
    elif command == "demo":
        cmd_demo()
    elif command in ["help", "-h", "--help"]:
        cmd_help()
    else:
        print(f"❌ Bilinmeyen komut: {command}")
        cmd_help()


if __name__ == "__main__":
    main()
