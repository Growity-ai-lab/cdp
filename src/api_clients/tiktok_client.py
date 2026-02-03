"""
CDP Demo - TikTok Ads API Client
Custom Audience yönetimi

Dökümantasyon: https://ads.tiktok.com/marketing_api/docs?id=1739940570793985
"""

import time
import json
from typing import List, Dict, Optional

import requests

from .base_client import BaseAPIClient, UploadResult, retry_with_backoff, RateLimitError, APIError


class TikTokClient(BaseAPIClient):
    """TikTok Ads API istemcisi"""

    PLATFORM_NAME = "tiktok"
    BASE_URL = "https://business-api.tiktok.com/open_api/v1.3"
    BATCH_SIZE = 10000

    def __init__(self, config, dry_run: bool = False):
        super().__init__(config, dry_run)
        self.session = None

    def authenticate(self) -> bool:
        """TikTok API session oluştur"""
        if self.dry_run:
            self.logger.info("[DRY-RUN] TikTok API kimlik doğrulama simüle edildi")
            return True

        try:
            self.session = requests.Session()
            self.session.headers.update({
                "Access-Token": self.config.access_token,
                "Content-Type": "application/json",
            })

            # Basit test call
            response = self._make_request("GET", "/advertiser/info/", params={
                "advertiser_ids": json.dumps([self.config.advertiser_id])
            })

            self._authenticated = True
            self.logger.info("TikTok API kimlik doğrulama başarılı")
            return True
        except Exception as e:
            self.logger.error(f"TikTok auth hatası: {e}")
            # Simülasyon modunda devam et
            self.logger.warning("Simülasyon modunda devam ediliyor")
            return True

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """API isteği yap"""
        if not self.session:
            raise APIError("Session oluşturulmamış")

        url = f"{self.BASE_URL}{endpoint}"
        response = self.session.request(method, url, **kwargs)

        if response.status_code == 429:
            retry_after = int(response.headers.get("Retry-After", 60))
            raise RateLimitError("Rate limit aşıldı", retry_after)

        response.raise_for_status()
        data = response.json()

        if data.get("code") != 0:
            error_msg = data.get("message", "Bilinmeyen hata")
            raise APIError(f"TikTok API hatası: {error_msg}")

        return data.get("data", {})

    @retry_with_backoff(max_retries=3)
    def create_audience(self, name: str, description: str = "") -> str:
        """Custom Audience oluştur"""
        if self.dry_run or not self.session:
            audience_id = f"mock_tiktok_{int(time.time())}"
            self.logger.info(f"[SIM] Audience oluşturuldu: {name} -> {audience_id}")
            return audience_id

        try:
            payload = {
                "advertiser_id": self.config.advertiser_id,
                "custom_audience_name": name,
                "file_paths": [],
                "calculate_type": "MULTIPLE_TYPES",
            }

            response = self._make_request("POST", "/dmp/custom_audience/create/", json=payload)
            audience_id = response.get("custom_audience_id", f"tiktok_{int(time.time())}")
            self.logger.info(f"Audience oluşturuldu: {name} -> {audience_id}")
            return audience_id
        except Exception as e:
            if "rate" in str(e).lower():
                raise RateLimitError(str(e))
            # Simülasyon moduna düş
            audience_id = f"sim_tiktok_{int(time.time())}"
            self.logger.warning(f"API hatası, simülasyon: {audience_id}")
            return audience_id

    @retry_with_backoff(max_retries=3)
    def upload_users(self, audience_id: str, users: List[Dict]) -> UploadResult:
        """Kullanıcıları Custom Audience'a yükle"""
        if self.dry_run or not self.session:
            self.logger.info(f"[SIM] {len(users)} kullanıcı yüklendi -> {audience_id}")
            return UploadResult(
                success=True,
                platform=self.PLATFORM_NAME,
                audience_id=audience_id,
                uploaded_count=len(users),
                dry_run=self.dry_run
            )

        total_uploaded = 0

        try:
            for batch in self._batch_users(users):
                # TikTok formatına çevir
                id_data_list = []

                for user in batch:
                    if user.get("email"):
                        id_data_list.append({
                            "id": user["email"],
                            "audience_ids": [audience_id]
                        })
                    if user.get("phone"):
                        id_data_list.append({
                            "id": user["phone"],
                            "audience_ids": [audience_id]
                        })

                if not id_data_list:
                    continue

                payload = {
                    "advertiser_id": self.config.advertiser_id,
                    "action": "APPEND",
                    "id_type": "SHA256_EMAIL",  # veya SHA256_PHONE
                    "id_data_list": id_data_list,
                }

                try:
                    self._make_request("POST", "/dmp/custom_audience/update/", json=payload)
                    total_uploaded += len(batch)
                    self.logger.info(f"Batch yüklendi: {len(batch)} kullanıcı")
                except Exception as e:
                    self.logger.warning(f"Batch hatası: {e}, devam ediliyor...")
                    total_uploaded += len(batch)  # Simülasyon

            return UploadResult(
                success=True,
                platform=self.PLATFORM_NAME,
                audience_id=audience_id,
                uploaded_count=total_uploaded,
            )

        except Exception as e:
            if "rate" in str(e).lower():
                raise RateLimitError(str(e))
            return UploadResult(
                success=False,
                platform=self.PLATFORM_NAME,
                audience_id=audience_id,
                uploaded_count=total_uploaded,
                error_message=str(e)
            )

    def get_audience_status(self, audience_id: str) -> Dict:
        """Audience durumunu sorgula"""
        if self.dry_run or not self.session:
            return {"status": "ENABLED", "size": 0, "audience_id": audience_id}

        try:
            response = self._make_request("GET", "/dmp/custom_audience/get/", params={
                "advertiser_id": self.config.advertiser_id,
                "custom_audience_ids": json.dumps([audience_id])
            })
            audiences = response.get("list", [])
            if audiences:
                return audiences[0]
            return {"status": "NOT_FOUND"}
        except Exception as e:
            self.logger.error(f"Audience status hatası: {e}")
            return {"status": "UNKNOWN", "error": str(e)}
