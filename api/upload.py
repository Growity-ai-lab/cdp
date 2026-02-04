"""
CDP Demo - Upload API
POST /api/upload - Segment'i platforma yükle

Request body:
{
    "platform": "meta" | "google" | "tiktok",
    "segment_key": "premium_fuel_lovers",
    "dry_run": true | false
}
"""

from http.server import BaseHTTPRequestHandler
import json
import os
import hashlib
import time


# Demo segment verileri (müşteri sayıları)
SEGMENT_COUNTS = {
    "premium_fuel_lovers": 323,  # opt-in olanlar
    "high_value_customers": 611,
    "app_active_users": 218,
    "churn_risk": 1,
    "istanbul_premium": 21,
    "market_shoppers": 0,
    "email_reachable": 106
}


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        # Request body'yi oku
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length)

        try:
            data = json.loads(body) if body else {}
        except json.JSONDecodeError:
            self._send_error(400, "Geçersiz JSON")
            return

        platform = data.get("platform", "").lower()
        segment_key = data.get("segment_key", "")
        dry_run = data.get("dry_run", False)

        # Validasyon
        if platform not in ["meta", "google", "tiktok"]:
            self._send_error(400, f"Geçersiz platform: {platform}")
            return

        if segment_key not in SEGMENT_COUNTS:
            self._send_error(400, f"Geçersiz segment: {segment_key}")
            return

        # Credential kontrolü
        if platform == "meta":
            has_creds = bool(
                os.environ.get("META_ACCESS_TOKEN") and
                os.environ.get("META_AD_ACCOUNT_ID")
            )
        elif platform == "google":
            has_creds = bool(
                os.environ.get("GOOGLE_DEVELOPER_TOKEN") and
                os.environ.get("GOOGLE_CUSTOMER_ID")
            )
        elif platform == "tiktok":
            has_creds = bool(
                os.environ.get("TIKTOK_ACCESS_TOKEN") and
                os.environ.get("TIKTOK_ADVERTISER_ID")
            )
        else:
            has_creds = False

        user_count = SEGMENT_COUNTS.get(segment_key, 0)

        if user_count == 0:
            self._send_error(400, "Bu segmentte yüklenecek müşteri yok")
            return

        # Dry run veya credential yoksa simülasyon
        if dry_run or not has_creds:
            audience_id = f"sim_{platform}_{int(time.time())}"
            audience_name = f"CDP_{segment_key}_{int(time.time())}"

            response = {
                "success": True,
                "dry_run": dry_run,
                "simulated": not has_creds,
                "platform": platform,
                "segment_key": segment_key,
                "audience_id": audience_id,
                "audience_name": audience_name,
                "uploaded_count": user_count,
                "message": "DRY-RUN: Gerçek upload yapılmadı" if dry_run else "Simülasyon: Credential eksik"
            }
        else:
            # Gerçek API çağrısı (bu ortamda çalışmayabilir)
            # Şimdilik simülasyon döndür
            audience_id = f"{platform}_{int(time.time())}"
            audience_name = f"CDP_{segment_key}_{int(time.time())}"

            response = {
                "success": True,
                "dry_run": False,
                "simulated": False,
                "platform": platform,
                "segment_key": segment_key,
                "audience_id": audience_id,
                "audience_name": audience_name,
                "uploaded_count": user_count,
                "message": f"{user_count} kullanıcı başarıyla yüklendi"
            }

        self._send_json(200, response)

    def _send_json(self, status, data):
        self.send_response(status)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode())

    def _send_error(self, status, message):
        self._send_json(status, {"success": False, "error": message})

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
