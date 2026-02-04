"""
CDP Demo - Konfigürasyon Yönetimi
API credential'ları ve ayarlar için merkezi yönetim
"""

import os
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class MetaConfig:
    """Meta Marketing API konfigürasyonu"""
    app_id: str = ""
    app_secret: str = ""
    access_token: str = ""
    ad_account_id: str = ""  # act_XXXXXXXXXX formatında
    api_version: str = "v18.0"

    @classmethod
    def from_env(cls) -> "MetaConfig":
        return cls(
            app_id=os.getenv("META_APP_ID", ""),
            app_secret=os.getenv("META_APP_SECRET", ""),
            access_token=os.getenv("META_ACCESS_TOKEN", ""),
            ad_account_id=os.getenv("META_AD_ACCOUNT_ID", ""),
        )

    def is_valid(self) -> bool:
        return all([self.access_token, self.ad_account_id])


@dataclass
class GoogleConfig:
    """Google Ads API konfigürasyonu"""
    developer_token: str = ""
    client_id: str = ""
    client_secret: str = ""
    refresh_token: str = ""
    customer_id: str = ""  # XXXXXXXXXX (tiresiz)
    login_customer_id: str = ""  # MCC hesabı için

    @classmethod
    def from_env(cls) -> "GoogleConfig":
        return cls(
            developer_token=os.getenv("GOOGLE_DEVELOPER_TOKEN", ""),
            client_id=os.getenv("GOOGLE_CLIENT_ID", ""),
            client_secret=os.getenv("GOOGLE_CLIENT_SECRET", ""),
            refresh_token=os.getenv("GOOGLE_REFRESH_TOKEN", ""),
            customer_id=os.getenv("GOOGLE_CUSTOMER_ID", ""),
            login_customer_id=os.getenv("GOOGLE_LOGIN_CUSTOMER_ID", ""),
        )

    def is_valid(self) -> bool:
        return all([self.developer_token, self.client_id, self.client_secret,
                    self.refresh_token, self.customer_id])


@dataclass
class TikTokConfig:
    """TikTok Ads API konfigürasyonu"""
    access_token: str = ""
    advertiser_id: str = ""
    app_id: str = ""
    secret: str = ""

    @classmethod
    def from_env(cls) -> "TikTokConfig":
        return cls(
            access_token=os.getenv("TIKTOK_ACCESS_TOKEN", ""),
            advertiser_id=os.getenv("TIKTOK_ADVERTISER_ID", ""),
            app_id=os.getenv("TIKTOK_APP_ID", ""),
            secret=os.getenv("TIKTOK_SECRET", ""),
        )

    def is_valid(self) -> bool:
        return all([self.access_token, self.advertiser_id])


@dataclass
class CDPConfig:
    """Ana CDP konfigürasyonu"""
    meta: MetaConfig = field(default_factory=MetaConfig)
    google: GoogleConfig = field(default_factory=GoogleConfig)
    tiktok: TikTokConfig = field(default_factory=TikTokConfig)

    # Genel ayarlar
    dry_run: bool = False
    log_level: str = "INFO"
    retry_count: int = 3
    retry_delay: float = 1.0

    @classmethod
    def load(cls, env_path: str = ".env") -> "CDPConfig":
        """Konfigürasyonu .env dosyasından yükle"""
        env_file = Path(env_path)
        if env_file.exists():
            # Manuel .env parsing (python-dotenv opsiyonel)
            with open(env_file, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        os.environ[key.strip()] = value.strip()

        return cls(
            meta=MetaConfig.from_env(),
            google=GoogleConfig.from_env(),
            tiktok=TikTokConfig.from_env(),
            dry_run=os.getenv("CDP_DRY_RUN", "false").lower() == "true",
            log_level=os.getenv("CDP_LOG_LEVEL", "INFO"),
        )

    def validate_platform(self, platform: str) -> tuple:
        """Platform credential'larını kontrol et"""
        if platform == "meta":
            if not self.meta.is_valid():
                return False, "Meta API credential'ları eksik (ACCESS_TOKEN, AD_ACCOUNT_ID)"
        elif platform == "google":
            if not self.google.is_valid():
                return False, "Google Ads API credential'ları eksik"
        elif platform == "tiktok":
            if not self.tiktok.is_valid():
                return False, "TikTok API credential'ları eksik (ACCESS_TOKEN, ADVERTISER_ID)"
        else:
            return False, f"Bilinmeyen platform: {platform}"
        return True, "OK"


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """Logging yapılandırması"""
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    formatter = logging.Formatter(
        "%(asctime)s | %(name)s | %(levelname)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # File handler
    file_handler = logging.FileHandler(
        log_dir / "cdp_api.log",
        encoding="utf-8"
    )
    file_handler.setFormatter(formatter)

    # Root logger
    logger = logging.getLogger("cdp")
    logger.setLevel(getattr(logging, log_level.upper()))
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger
