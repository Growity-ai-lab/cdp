#!/usr/bin/env python3
"""
CDP Demo - Ana Uygulama
Basit CDP sistemi demonstrasyonu

Kullanım:
  python main.py generate    # Mock veri oluştur
  python main.py segments    # Segmentleri listele ve çalıştır
  python main.py export      # Tüm segmentleri platformlara export et
  python main.py export premium_fuel_lovers  # Tek segment export
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


def cmd_help():
    """Yardım mesajı"""
    print("""
CDP Demo - Basit Customer Data Platform Demonstrasyonu

Kullanım:
  python main.py <komut> [argümanlar]

Komutlar:
  generate              Mock veri oluştur (1000 müşteri, 90 günlük işlem)
  segments              Tüm segmentleri listele ve analiz et
  export [segment]      Segment(ler)i Meta/Google/TikTok'a export et
  demo                  Interaktif demo - tüm akışı göster
  help                  Bu yardım mesajını göster

Örnekler:
  python main.py demo                           # Tam demo
  python main.py generate                       # Sadece veri oluştur
  python main.py segments                       # Segmentleri analiz et
  python main.py export                         # Tüm segmentleri export et
  python main.py export premium_fuel_lovers     # Tek segment export et

Segment isimleri:
  - premium_fuel_lovers   : Premium yakıt alan müşteriler
  - high_value_customers  : Yüksek harcama yapanlar
  - app_active_users      : Aktif app kullanıcıları
  - churn_risk            : Kaybetme riski olanlar
  - istanbul_premium      : İstanbul'daki premium müşteriler
  - market_shoppers       : Market alışverişi yapanlar
  - email_reachable       : Email ile ulaşılabilir premium müşteriler
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
    elif command == "demo":
        cmd_demo()
    elif command in ["help", "-h", "--help"]:
        cmd_help()
    else:
        print(f"❌ Bilinmeyen komut: {command}")
        cmd_help()


if __name__ == "__main__":
    main()
