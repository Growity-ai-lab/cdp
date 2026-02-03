"""
CDP Demo - Base API Client
Tüm platform istemcileri için ortak işlevsellik
"""

import time
import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from functools import wraps


@dataclass
class UploadResult:
    """API upload sonucu"""
    success: bool
    platform: str
    audience_id: Optional[str] = None
    audience_name: Optional[str] = None
    matched_count: int = 0
    uploaded_count: int = 0
    error_message: Optional[str] = None
    dry_run: bool = False

    def __str__(self) -> str:
        if self.success:
            status = "[DRY-RUN] " if self.dry_run else ""
            return f"{status}✅ {self.platform.upper()}: {self.uploaded_count} kullanıcı yüklendi"
        return f"❌ {self.platform.upper()}: {self.error_message}"


class RateLimitError(Exception):
    """Rate limit aşıldı hatası"""
    def __init__(self, message: str, retry_after: Optional[float] = None):
        super().__init__(message)
        self.retry_after = retry_after


class RetryableError(Exception):
    """Tekrar denenebilir hata"""
    pass


class APIError(Exception):
    """Genel API hatası"""
    pass


def retry_with_backoff(max_retries: int = 3, base_delay: float = 1.0):
    """Exponential backoff ile retry decorator"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            logger = logging.getLogger("cdp.retry")

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except RateLimitError as e:
                    wait_time = e.retry_after or (base_delay * (2 ** attempt))
                    logger.warning(f"Rate limit: {wait_time:.1f}s bekleniyor...")
                    time.sleep(wait_time)
                    last_exception = e
                except RetryableError as e:
                    wait_time = base_delay * (2 ** attempt)
                    logger.warning(f"Retry {attempt + 1}/{max_retries}: {e}")
                    time.sleep(wait_time)
                    last_exception = e
                except Exception as e:
                    # Diğer hatalar için retry yapma
                    raise

            if last_exception:
                raise last_exception
            raise APIError("Maksimum retry sayısına ulaşıldı")

        return wrapper
    return decorator


class BaseAPIClient(ABC):
    """Tüm API istemcileri için base class"""

    PLATFORM_NAME: str = "base"
    BATCH_SIZE: int = 10000

    def __init__(self, config: Any, dry_run: bool = False):
        self.config = config
        self.dry_run = dry_run
        self.logger = logging.getLogger(f"cdp.{self.PLATFORM_NAME}")
        self._authenticated = False

    @abstractmethod
    def authenticate(self) -> bool:
        """API ile kimlik doğrulama"""
        pass

    @abstractmethod
    def create_audience(self, name: str, description: str = "") -> str:
        """Yeni custom audience oluştur, audience_id döndür"""
        pass

    @abstractmethod
    def upload_users(self, audience_id: str, users: List[Dict]) -> UploadResult:
        """Hash'lenmiş kullanıcı listesini yükle"""
        pass

    @abstractmethod
    def get_audience_status(self, audience_id: str) -> Dict:
        """Audience durumunu sorgula"""
        pass

    def upload_segment(
        self,
        segment_name: str,
        users: List[Dict],
        description: str = ""
    ) -> UploadResult:
        """
        Segment'i platforma yükle (high-level method)

        Args:
            segment_name: Segment adı
            users: Hash'lenmiş kullanıcı listesi [{"email": "hash", "phone": "hash"}, ...]
            description: Audience açıklaması

        Returns:
            UploadResult: Upload sonucu
        """
        if not users:
            return UploadResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error_message="Yüklenecek kullanıcı yok"
            )

        if self.dry_run:
            self.logger.info(f"[DRY-RUN] {len(users)} kullanıcı yüklenecekti: {segment_name}")
            return UploadResult(
                success=True,
                platform=self.PLATFORM_NAME,
                audience_name=f"CDP_{segment_name}",
                uploaded_count=len(users),
                dry_run=True
            )

        try:
            # 1. Authenticate
            self.logger.info("Kimlik doğrulanıyor...")
            if not self.authenticate():
                return UploadResult(
                    success=False,
                    platform=self.PLATFORM_NAME,
                    error_message="Kimlik doğrulama başarısız"
                )

            # 2. Create audience
            audience_name = f"CDP_{segment_name}_{int(time.time())}"
            self.logger.info(f"Audience oluşturuluyor: {audience_name}")
            audience_id = self.create_audience(audience_name, description)

            # 3. Upload users
            self.logger.info(f"{len(users)} kullanıcı yükleniyor...")
            result = self.upload_users(audience_id, users)
            result.audience_name = audience_name

            return result

        except RateLimitError as e:
            self.logger.error(f"Rate limit hatası: {e}")
            return UploadResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error_message=f"Rate limit: {e}"
            )
        except Exception as e:
            self.logger.error(f"Upload hatası: {e}")
            return UploadResult(
                success=False,
                platform=self.PLATFORM_NAME,
                error_message=str(e)
            )

    def _batch_users(self, users: List[Dict]) -> List[List[Dict]]:
        """Kullanıcı listesini batch'lere böl"""
        return [
            users[i:i + self.BATCH_SIZE]
            for i in range(0, len(users), self.BATCH_SIZE)
        ]
