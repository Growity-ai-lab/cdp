"""
CDP Demo - Platform Export Modülü
Segmentleri Meta, Google, TikTok formatında export etme
"""

import csv
import json
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass

from segment_engine import SegmentEngine, PREDEFINED_SEGMENTS, SegmentDefinition


@dataclass
class ExportConfig:
    """Export konfigürasyonu"""
    platform: str  # meta, google, tiktok
    include_email: bool = True
    include_phone: bool = True
    include_name: bool = False  # Meta için opsiyonel
    include_city: bool = False  # Meta için opsiyonel
    hash_algorithm: str = "sha256"


class PlatformExporter:
    """Platform export işlemleri"""
    
    PLATFORM_CONFIGS = {
        "meta": {
            "name": "Meta (Facebook/Instagram)",
            "file_format": "csv",
            "hash_required": True,
            "supported_fields": ["email", "phone", "fn", "ln", "ct", "st", "zip", "country", "dob", "gen"],
            "documentation": "https://developers.facebook.com/docs/marketing-api/audiences/guides/custom-audiences"
        },
        "google": {
            "name": "Google Ads Customer Match",
            "file_format": "csv",
            "hash_required": True,
            "supported_fields": ["Email", "Phone", "First Name", "Last Name", "Country", "Zip"],
            "documentation": "https://support.google.com/google-ads/answer/6276125"
        },
        "tiktok": {
            "name": "TikTok Custom Audiences",
            "file_format": "csv",
            "hash_required": True,
            "supported_fields": ["IDFA", "GAID", "EMAIL_SHA256", "PHONE_SHA256"],
            "documentation": "https://ads.tiktok.com/marketing_api/docs?id=1739940570793985"
        },
    }
    
    def __init__(self, data_dir: str = "data", export_dir: str = "exports"):
        self.data_dir = Path(data_dir)
        self.export_dir = Path(export_dir)
        self.export_dir.mkdir(exist_ok=True)
        self.engine = SegmentEngine(data_dir)
    
    def _hash_value(self, value: str, algorithm: str = "sha256") -> str:
        """Değeri hash'le"""
        if not value:
            return ""
        # Normalize: lowercase, strip whitespace
        normalized = value.lower().strip()
        if algorithm == "sha256":
            return hashlib.sha256(normalized.encode()).hexdigest()
        elif algorithm == "md5":
            return hashlib.md5(normalized.encode()).hexdigest()
        return normalized
    
    def _normalize_phone(self, phone: str) -> str:
        """Telefon numarasını normalize et"""
        if not phone:
            return ""
        # Sadece rakamları al
        digits = ''.join(filter(str.isdigit, phone))
        # Türkiye kodu ekle
        if digits.startswith("90"):
            return digits
        elif digits.startswith("0"):
            return "90" + digits[1:]
        return "90" + digits
    
    def export_for_meta(self, segment_results: List[Dict], segment_name: str, config: Optional[ExportConfig] = None) -> str:
        """Meta Custom Audience formatında export"""
        if config is None:
            config = ExportConfig(platform="meta")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"meta_audience_{segment_name}_{timestamp}.csv"
        filepath = self.export_dir / filename
        
        # Meta formatı: email, phone, fn (first name), ln (last name), ct (city)
        rows = []
        for customer in segment_results:
            row = {}
            
            if config.include_email and customer.get("email"):
                row["email"] = self._hash_value(customer["email"])
            
            if config.include_phone and customer.get("phone"):
                row["phone"] = self._hash_value(self._normalize_phone(customer["phone"]))
            
            if config.include_name:
                if customer.get("first_name"):
                    row["fn"] = self._hash_value(customer["first_name"])
                if customer.get("last_name"):
                    row["ln"] = self._hash_value(customer["last_name"])
            
            if config.include_city and customer.get("city"):
                row["ct"] = self._hash_value(customer["city"])
            
            if row:  # En az bir alan varsa ekle
                rows.append(row)
        
        # CSV yaz
        if rows:
            fieldnames = list(rows[0].keys())
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        return str(filepath)
    
    def export_for_google(self, segment_results: List[Dict], segment_name: str, config: Optional[ExportConfig] = None) -> str:
        """Google Ads Customer Match formatında export"""
        if config is None:
            config = ExportConfig(platform="google")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"google_audience_{segment_name}_{timestamp}.csv"
        filepath = self.export_dir / filename
        
        rows = []
        for customer in segment_results:
            row = {}
            
            if config.include_email and customer.get("email"):
                row["Email"] = self._hash_value(customer["email"])
            
            if config.include_phone and customer.get("phone"):
                row["Phone"] = self._hash_value(self._normalize_phone(customer["phone"]))
            
            if config.include_name:
                if customer.get("first_name"):
                    row["First Name"] = self._hash_value(customer["first_name"])
                if customer.get("last_name"):
                    row["Last Name"] = self._hash_value(customer["last_name"])
            
            row["Country"] = "TR"
            
            if row:
                rows.append(row)
        
        # CSV yaz
        if rows:
            fieldnames = list(rows[0].keys())
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        return str(filepath)
    
    def export_for_tiktok(self, segment_results: List[Dict], segment_name: str, config: Optional[ExportConfig] = None) -> str:
        """TikTok Custom Audience formatında export"""
        if config is None:
            config = ExportConfig(platform="tiktok")
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"tiktok_audience_{segment_name}_{timestamp}.csv"
        filepath = self.export_dir / filename
        
        rows = []
        for customer in segment_results:
            row = {}
            
            if config.include_email and customer.get("email"):
                row["EMAIL_SHA256"] = self._hash_value(customer["email"])
            
            if config.include_phone and customer.get("phone"):
                row["PHONE_SHA256"] = self._hash_value(self._normalize_phone(customer["phone"]))
            
            if row:
                rows.append(row)
        
        # CSV yaz
        if rows:
            fieldnames = list(rows[0].keys())
            with open(filepath, "w", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(rows)
        
        return str(filepath)
    
    def export_segment(self, segment_key: str, platforms: List[str] = None) -> Dict[str, str]:
        """Bir segmenti belirtilen platformlara export et"""
        if platforms is None:
            platforms = ["meta", "google", "tiktok"]
        
        if segment_key not in PREDEFINED_SEGMENTS:
            raise ValueError(f"Bilinmeyen segment: {segment_key}")
        
        segment = PREDEFINED_SEGMENTS[segment_key]
        results = self.engine.run_segment(segment)
        
        if not results:
            print(f"⚠️  Segment '{segment.name}' boş, export yapılmadı.")
            return {}
        
        exports = {}
        
        for platform in platforms:
            if platform == "meta":
                exports["meta"] = self.export_for_meta(results, segment_key)
            elif platform == "google":
                exports["google"] = self.export_for_google(results, segment_key)
            elif platform == "tiktok":
                exports["tiktok"] = self.export_for_tiktok(results, segment_key)
        
        return exports
    
    def export_all_segments(self, platforms: List[str] = None) -> Dict[str, Dict[str, str]]:
        """Tüm hazır segmentleri export et"""
        all_exports = {}
        
        for segment_key in PREDEFINED_SEGMENTS:
            try:
                exports = self.export_segment(segment_key, platforms)
                if exports:
                    all_exports[segment_key] = exports
            except Exception as e:
                print(f"❌ {segment_key} export hatası: {e}")
        
        return all_exports
    
    def generate_summary_report(self, exports: Dict[str, Dict[str, str]]) -> str:
        """Export özet raporu oluştur"""
        report_lines = [
            "=" * 70,
            "CDP DEMO - EXPORT ÖZET RAPORU",
            f"Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "=" * 70,
            ""
        ]
        
        for segment_key, platforms in exports.items():
            segment = PREDEFINED_SEGMENTS[segment_key]
            results = self.engine.run_segment(segment)
            stats = self.engine.get_segment_stats(results)
            
            report_lines.append(f"📊 {segment.name}")
            report_lines.append(f"   Açıklama: {segment.description}")
            report_lines.append(f"   Müşteri Sayısı: {stats['count']}")
            report_lines.append(f"   Export Dosyaları:")
            
            for platform, filepath in platforms.items():
                platform_name = self.PLATFORM_CONFIGS[platform]["name"]
                report_lines.append(f"      - {platform_name}: {filepath}")
            
            report_lines.append("")
        
        report_lines.extend([
            "=" * 70,
            "KULLANIM TALİMATLARI",
            "=" * 70,
            "",
            "Meta (Facebook/Instagram):",
            "  1. Business Manager > Audiences > Create Audience > Custom Audience",
            "  2. Customer List seç",
            "  3. CSV dosyasını yükle",
            "  4. 'Data is hashed' seçeneğini işaretle",
            "",
            "Google Ads:",
            "  1. Tools > Audience Manager > Customer Lists",
            "  2. + butonuna tıkla",
            "  3. 'Upload customer emails' seç",
            "  4. CSV dosyasını yükle",
            "",
            "TikTok Ads:",
            "  1. Assets > Audiences > Create Audience",
            "  2. Customer File seç",
            "  3. CSV dosyasını yükle",
            "",
        ])
        
        report = "\n".join(report_lines)
        
        # Raporu kaydet
        report_path = self.export_dir / f"export_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(report)
        
        return report


if __name__ == "__main__":
    print("🚀 CDP Demo - Platform Export")
    print("=" * 60)
    
    exporter = PlatformExporter("data", "exports")
    
    # Tek bir segment export et
    print("\n📤 Premium Yakıt Severler segmenti export ediliyor...")
    exports = exporter.export_segment("premium_fuel_lovers", ["meta", "google", "tiktok"])
    
    for platform, filepath in exports.items():
        print(f"   ✅ {platform}: {filepath}")
    
    # Özet rapor
    print("\n" + "=" * 60)
    print("\n📋 Tüm segmentler export ediliyor...")
    all_exports = exporter.export_all_segments()
    
    report = exporter.generate_summary_report(all_exports)
    print(report)
