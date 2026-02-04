"""
CDP Demo - Meta Marketing API Client
Facebook/Instagram Custom Audiences yönetimi

Dökümantasyon: https://developers.facebook.com/docs/marketing-api/audiences
"""

import time
from typing import List, Dict, Optional

from .base_client import BaseAPIClient, UploadResult, retry_with_backoff, RateLimitError, APIError

# Facebook Business SDK (opsiyonel)
try:
    from facebook_business.api import FacebookAdsApi
    from facebook_business.adobjects.adaccount import AdAccount
    from facebook_business.adobjects.customaudience import CustomAudience
    HAS_FB_SDK = True
except ImportError:
    HAS_FB_SDK = False


class MetaClient(BaseAPIClient):
    """Meta Marketing API istemcisi"""

    PLATFORM_NAME = "meta"
    BATCH_SIZE = 10000  # Meta max batch boyutu

    def __init__(self, config, dry_run: bool = False):
        super().__init__(config, dry_run)
        self.api = None
        self.ad_account = None

    def authenticate(self) -> bool:
        """Facebook Ads API ile kimlik doğrulama"""
        if self.dry_run:
            self.logger.info("[DRY-RUN] Meta API kimlik doğrulama simüle edildi")
            return True

        if not HAS_FB_SDK:
            self.logger.warning("facebook-business SDK yüklü değil, simülasyon modunda çalışıyor")
            return True

        try:
            FacebookAdsApi.init(
                app_id=self.config.app_id,
                app_secret=self.config.app_secret,
                access_token=self.config.access_token,
            )
            self.ad_account = AdAccount(self.config.ad_account_id)
            self._authenticated = True
            self.logger.info("Meta API kimlik doğrulama başarılı")
            return True
        except Exception as e:
            self.logger.error(f"Meta auth hatası: {e}")
            return False

    @retry_with_backoff(max_retries=3)
    def create_audience(self, name: str, description: str = "") -> str:
        """Custom Audience oluştur"""
        if self.dry_run or not HAS_FB_SDK:
            audience_id = f"mock_meta_{int(time.time())}"
            self.logger.info(f"[SIM] Audience oluşturuldu: {name} -> {audience_id}")
            return audience_id

        try:
            params = {
                "name": name,
                "subtype": "CUSTOM",
                "description": description or "CDP tarafından oluşturuldu",
                "customer_file_source": "USER_PROVIDED_ONLY",
            }
            audience = self.ad_account.create_custom_audience(params=params)
            audience_id = audience["id"]
            self.logger.info(f"Audience oluşturuldu: {name} -> {audience_id}")
            return audience_id
        except Exception as e:
            if "rate limit" in str(e).lower():
                raise RateLimitError(str(e))
            raise APIError(f"Audience oluşturma hatası: {e}")

    @retry_with_backoff(max_retries=3)
    def upload_users(self, audience_id: str, users: List[Dict]) -> UploadResult:
        """
        Kullanıcıları Custom Audience'a yükle

        users format: [{"email": "hash...", "phone": "hash..."}, ...]
        """
        if self.dry_run or not HAS_FB_SDK:
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
            # Batch'ler halinde yükle
            for batch in self._batch_users(users):
                # Meta formatına çevir
                schema = ["EMAIL", "PHONE"]
                data = []

                for user in batch:
                    row = [
                        user.get("email", ""),
                        user.get("phone", "")
                    ]
                    # Boş olmayan değerler varsa ekle
                    if any(row):
                        data.append(row)

                if not data:
                    continue

                payload = {
                    "payload": {
                        "schema": schema,
                        "data": data,
                    }
                }

                audience = CustomAudience(audience_id)
                audience.create_user(params=payload)

                total_uploaded += len(data)
                self.logger.info(f"Batch yüklendi: {len(data)} kullanıcı")

            return UploadResult(
                success=True,
                platform=self.PLATFORM_NAME,
                audience_id=audience_id,
                uploaded_count=total_uploaded,
            )

        except Exception as e:
            if "rate limit" in str(e).lower():
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
        if self.dry_run or not HAS_FB_SDK:
            return {"status": "READY", "approximate_count": 0, "id": audience_id}

        try:
            audience = CustomAudience(audience_id)
            info = audience.api_get(fields=[
                "name", "approximate_count", "delivery_status", "operation_status"
            ])
            return dict(info)
        except Exception as e:
            self.logger.error(f"Audience status hatası: {e}")
            return {"status": "UNKNOWN", "error": str(e)}
