"""
CDP Demo - Segments API
GET /api/segments - Tüm segmentleri listele
GET /api/segments?key=premium_fuel_lovers - Tek segment detayı
"""

from http.server import BaseHTTPRequestHandler
import json
import sys
from pathlib import Path
from urllib.parse import urlparse, parse_qs

# src klasörünü path'e ekle
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

# Demo verileri (serverless'da dosya sistemi olmayabilir)
DEMO_SEGMENTS = {
    "premium_fuel_lovers": {
        "name": "Premium Yakıt Severler",
        "description": "Son 90 günde 3+ kez premium yakıt alan müşteriler",
        "count": 478,
        "percentage": 47.8,
        "total_revenue": 18955420,
        "has_app_pct": 35.8,
        "cities": {"Bursa": 102, "Ankara": 100, "İstanbul": 96, "Antalya": 92, "İzmir": 88}
    },
    "high_value_customers": {
        "name": "Yüksek Değerli Müşteriler",
        "description": "Son 90 günde 5000 TL üzeri harcama yapan müşteriler",
        "count": 900,
        "percentage": 90.0,
        "total_revenue": 25790604,
        "has_app_pct": 35.7,
        "cities": {"Ankara": 187, "Antalya": 185, "Bursa": 183, "İstanbul": 178, "İzmir": 167}
    },
    "app_active_users": {
        "name": "Aktif App Kullanıcıları",
        "description": "App'i olan ve son 30 günde 5+ event üreten müşteriler",
        "count": 322,
        "percentage": 32.2,
        "total_revenue": 8535360,
        "has_app_pct": 100.0,
        "cities": {"Ankara": 74, "İstanbul": 70, "Bursa": 62, "Antalya": 60, "İzmir": 56}
    },
    "churn_risk": {
        "name": "Churn Riski",
        "description": "Eskiden düzenli gelip son 60 günde gelmeyen müşteriler",
        "count": 1,
        "percentage": 0.1,
        "total_revenue": 0,
        "has_app_pct": 100.0,
        "cities": {"Ankara": 1}
    },
    "istanbul_premium": {
        "name": "İstanbul Premium",
        "description": "İstanbul'da yaşayan premium segment müşteriler",
        "count": 30,
        "percentage": 3.0,
        "total_revenue": 1925189,
        "has_app_pct": 33.3,
        "cities": {"İstanbul": 30}
    },
    "market_shoppers": {
        "name": "Market Alışverişçileri",
        "description": "Son 30 günde 3+ kez market alışverişi yapan müşteriler",
        "count": 0,
        "percentage": 0,
        "total_revenue": 0,
        "has_app_pct": 0,
        "cities": {}
    },
    "email_reachable": {
        "name": "Email ile Ulaşılabilir",
        "description": "Email opt-in vermiş ve premium segment müşteriler",
        "count": 106,
        "percentage": 10.6,
        "total_revenue": 6460362,
        "has_app_pct": 34.9,
        "cities": {"Ankara": 24, "İstanbul": 23, "Bursa": 22, "Antalya": 20, "İzmir": 17}
    }
}

DEMO_SUMMARY = {
    "total_customers": 1000,
    "total_transactions": 14250,
    "total_events": 13992,
    "total_revenue": 28500000,
    "premium_customers": 153,
    "regular_customers": 300,
    "occasional_customers": 547,
    "app_users": 353,
    "email_opted_in": 700,
    "cities": {
        "İstanbul": 200,
        "Ankara": 200,
        "İzmir": 200,
        "Bursa": 200,
        "Antalya": 200
    }
}


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        # CORS headers
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Parse query params
        parsed = urlparse(self.path)
        params = parse_qs(parsed.query)

        # Tek segment mi tüm liste mi?
        if 'key' in params:
            segment_key = params['key'][0]
            if segment_key in DEMO_SEGMENTS:
                response = {
                    "success": True,
                    "segment": {
                        "key": segment_key,
                        **DEMO_SEGMENTS[segment_key]
                    }
                }
            else:
                response = {
                    "success": False,
                    "error": f"Segment bulunamadı: {segment_key}"
                }
        else:
            # Tüm segmentler + özet
            response = {
                "success": True,
                "summary": DEMO_SUMMARY,
                "segments": [
                    {"key": k, **v}
                    for k, v in DEMO_SEGMENTS.items()
                ]
            }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
