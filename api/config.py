"""
CDP Demo - Config API
GET /api/config - Platform credential durumlarını kontrol et
"""

from http.server import BaseHTTPRequestHandler
import json
import os


class handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        # Platform credential kontrolü
        platforms = {
            "meta": {
                "name": "Meta (Facebook/Instagram)",
                "configured": bool(
                    os.environ.get("META_ACCESS_TOKEN") and
                    os.environ.get("META_AD_ACCOUNT_ID")
                ),
                "icon": "📘"
            },
            "google": {
                "name": "Google Ads",
                "configured": bool(
                    os.environ.get("GOOGLE_DEVELOPER_TOKEN") and
                    os.environ.get("GOOGLE_CUSTOMER_ID")
                ),
                "icon": "🔍"
            },
            "tiktok": {
                "name": "TikTok Ads",
                "configured": bool(
                    os.environ.get("TIKTOK_ACCESS_TOKEN") and
                    os.environ.get("TIKTOK_ADVERTISER_ID")
                ),
                "icon": "🎵"
            }
        }

        configured_count = sum(1 for p in platforms.values() if p["configured"])

        response = {
            "success": True,
            "platforms": platforms,
            "configured_count": configured_count,
            "total_count": len(platforms)
        }

        self.wfile.write(json.dumps(response, ensure_ascii=False).encode())

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
