"""
Uygulama Konfigürasyonu
"""
from pydantic_settings import BaseSettings
from typing import Optional
from functools import lru_cache


class Settings(BaseSettings):
    """Uygulama ayarları - .env dosyasından okunur"""
    
    # Environment
    ENV: str = "development"
    DEBUG: bool = True
    
    # Server
    HOST: str = "0.0.0.0"
    PORT: int = 3000
    
    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:password@localhost:5432/oldunmu_db"
    
    # JWT
    JWT_SECRET_KEY: str = "your-super-secret-jwt-key"
    JWT_REFRESH_SECRET_KEY: str = "your-super-secret-refresh-key"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # Email
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: Optional[str] = None
    SMTP_PASSWORD: Optional[str] = None
    EMAIL_FROM: str = "Öldün mü? <noreply@oldunmu.tr>"
    
    # SMS (Twilio)
    TWILIO_ACCOUNT_SID: Optional[str] = None
    TWILIO_AUTH_TOKEN: Optional[str] = None
    TWILIO_PHONE_NUMBER: Optional[str] = None
    
    # FCM
    FCM_SERVER_KEY: Optional[str] = None
    
    # File Upload
    MAX_FILE_SIZE: int = 5 * 1024 * 1024  # 5MB
    UPLOAD_DIR: str = "./uploads"
    
    # Rate Limiting
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60
    
    # URLs
    FRONTEND_URL: str = "http://localhost:3001"
    APP_URL: str = "https://oldunmu.tr"
    
    # Check-in defaults (hours)
    DEFAULT_CHECKIN_INTERVAL: int = 24
    WARNING_THRESHOLD: int = 44
    ALARM_THRESHOLD: int = 48
    
    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    """Singleton settings instance"""
    return Settings()


# Abonelik planları
SUBSCRIPTION_PLANS = [
    {
        "id": "ucretsiz",
        "ad": "Ücretsiz",
        "fiyat": 0,
        "para_birimi": "TRY",
        "periyot": None,
        "ozellikler": [
            "Günlük 1 check-in",
            "2 acil durum kişisi",
            "Temel bildirimler"
        ],
        "max_acil_kisi": 2,
    },
    {
        "id": "aylik_premium",
        "ad": "Premium Aylık",
        "fiyat": 49.99,
        "para_birimi": "TRY",
        "periyot": "aylik",
        "ozellikler": [
            "Sınırsız check-in",
            "5 acil durum kişisi",
            "Konum paylaşımı",
            "Özel hatırlatma zamanları",
            "Detaylı raporlar",
            "Öncelikli destek"
        ],
        "max_acil_kisi": 5,
    },
    {
        "id": "yillik_premium",
        "ad": "Premium Yıllık",
        "fiyat": 399.99,
        "para_birimi": "TRY",
        "periyot": "yillik",
        "indirim_yuzde": 33,
        "ozellikler": [
            "Tüm premium özellikler",
            "2 ay ücretsiz"
        ],
        "max_acil_kisi": 5,
    },
]
