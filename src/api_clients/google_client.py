"""
CDP Demo - Google Ads API Client
Customer Match audience yönetimi

Dökümantasyon: https://developers.google.com/google-ads/api/docs/remarketing/audience-types/customer-match
"""

import time
from typing import List, Dict, Optional

from .base_client import BaseAPIClient, UploadResult, retry_with_backoff, RateLimitError, APIError

# Google Ads SDK (opsiyonel)
try:
    from google.ads.googleads.client import GoogleAdsClient
    from google.ads.googleads.errors import GoogleAdsException
    HAS_GOOGLE_SDK = True
except ImportError:
    HAS_GOOGLE_SDK = False


class GoogleClient(BaseAPIClient):
    """Google Ads API istemcisi"""

    PLATFORM_NAME = "google"
    BATCH_SIZE = 100000  # Google batch limiti

    def __init__(self, config, dry_run: bool = False):
        super().__init__(config, dry_run)
        self.client = None

    def authenticate(self) -> bool:
        """Google Ads API ile kimlik doğrulama"""
        if self.dry_run:
            self.logger.info("[DRY-RUN] Google Ads API kimlik doğrulama simüle edildi")
            return True

        if not HAS_GOOGLE_SDK:
            self.logger.warning("google-ads SDK yüklü değil, simülasyon modunda çalışıyor")
            return True

        try:
            credentials = {
                "developer_token": self.config.developer_token,
                "client_id": self.config.client_id,
                "client_secret": self.config.client_secret,
                "refresh_token": self.config.refresh_token,
                "use_proto_plus": True,
            }
            if self.config.login_customer_id:
                credentials["login_customer_id"] = self.config.login_customer_id

            self.client = GoogleAdsClient.load_from_dict(credentials)
            self._authenticated = True
            self.logger.info("Google Ads API kimlik doğrulama başarılı")
            return True
        except Exception as e:
            self.logger.error(f"Google auth hatası: {e}")
            return False

    @retry_with_backoff(max_retries=3)
    def create_audience(self, name: str, description: str = "") -> str:
        """Customer Match User List oluştur"""
        if self.dry_run or not HAS_GOOGLE_SDK:
            resource_name = f"customers/{self.config.customer_id}/userLists/mock_{int(time.time())}"
            self.logger.info(f"[SIM] User list oluşturuldu: {name} -> {resource_name}")
            return resource_name

        try:
            user_list_service = self.client.get_service("UserListService")

            user_list_operation = self.client.get_type("UserListOperation")
            user_list = user_list_operation.create
            user_list.name = name
            user_list.description = description or "CDP tarafından oluşturuldu"
            user_list.membership_life_span = 10000  # Maximum gün
            user_list.crm_based_user_list.upload_key_type = (
                self.client.enums.CustomerMatchUploadKeyTypeEnum.CONTACT_INFO
            )

            response = user_list_service.mutate_user_lists(
                customer_id=self.config.customer_id,
                operations=[user_list_operation]
            )
            resource_name = response.results[0].resource_name
            self.logger.info(f"User list oluşturuldu: {name} -> {resource_name}")
            return resource_name
        except GoogleAdsException as e:
            if "RATE_LIMIT" in str(e):
                raise RateLimitError(str(e))
            raise APIError(f"User list oluşturma hatası: {e}")

    @retry_with_backoff(max_retries=3)
    def upload_users(self, audience_id: str, users: List[Dict]) -> UploadResult:
        """Kullanıcıları Customer Match listesine yükle"""
        if self.dry_run or not HAS_GOOGLE_SDK:
            self.logger.info(f"[SIM] {len(users)} kullanıcı yüklendi -> {audience_id}")
            return UploadResult(
                success=True,
                platform=self.PLATFORM_NAME,
                audience_id=audience_id,
                uploaded_count=len(users),
                dry_run=self.dry_run
            )

        try:
            offline_user_data_job_service = self.client.get_service(
                "OfflineUserDataJobService"
            )

            # Job oluştur
            job_operation = self.client.get_type("OfflineUserDataJob")
            job_operation.type_ = self.client.enums.OfflineUserDataJobTypeEnum.CUSTOMER_MATCH_USER_LIST
            job_operation.customer_match_user_list_metadata.user_list = audience_id

            create_response = offline_user_data_job_service.create_offline_user_data_job(
                customer_id=self.config.customer_id,
                job=job_operation
            )
            job_resource_name = create_response.resource_name
            self.logger.info(f"Job oluşturuldu: {job_resource_name}")

            # Kullanıcıları batch'ler halinde ekle
            total_uploaded = 0

            for batch in self._batch_users(users):
                operations = []

                for user in batch:
                    operation = self.client.get_type("OfflineUserDataJobOperation")
                    user_data = operation.create

                    if user.get("email"):
                        identifier = user_data.user_identifiers.add()
                        identifier.hashed_email = user["email"]

                    if user.get("phone"):
                        identifier = user_data.user_identifiers.add()
                        identifier.hashed_phone_number = user["phone"]

                    operations.append(operation)

                if operations:
                    offline_user_data_job_service.add_offline_user_data_job_operations(
                        resource_name=job_resource_name,
                        operations=operations
                    )
                    total_uploaded += len(operations)
                    self.logger.info(f"Batch yüklendi: {len(operations)} kullanıcı")

            # Job'ı çalıştır
            offline_user_data_job_service.run_offline_user_data_job(
                resource_name=job_resource_name
            )
            self.logger.info("Job çalıştırıldı, işleniyor...")

            return UploadResult(
                success=True,
                platform=self.PLATFORM_NAME,
                audience_id=audience_id,
                uploaded_count=total_uploaded,
            )

        except GoogleAdsException as e:
            if "RATE_LIMIT" in str(e):
                raise RateLimitError(str(e))
            return UploadResult(
                success=False,
                platform=self.PLATFORM_NAME,
                audience_id=audience_id,
                error_message=str(e)
            )

    def get_audience_status(self, audience_id: str) -> Dict:
        """User List durumunu sorgula"""
        if self.dry_run or not HAS_GOOGLE_SDK:
            return {"status": "OPEN", "size": 0, "resource_name": audience_id}

        try:
            ga_service = self.client.get_service("GoogleAdsService")
            query = f"""
                SELECT user_list.id, user_list.name, user_list.size_for_display
                FROM user_list
                WHERE user_list.resource_name = '{audience_id}'
            """
            response = ga_service.search(customer_id=self.config.customer_id, query=query)
            for row in response:
                return {
                    "id": row.user_list.id,
                    "name": row.user_list.name,
                    "size": row.user_list.size_for_display,
                }
            return {"status": "NOT_FOUND"}
        except Exception as e:
            self.logger.error(f"User list status hatası: {e}")
            return {"status": "UNKNOWN", "error": str(e)}
