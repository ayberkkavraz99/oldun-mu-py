"""
Güvenlik yardımcı fonksiyonları - JWT, şifre hashleme vb.
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid

from app.config import get_settings
from app.database import get_db
from app.models import Kullanici

settings = get_settings()

# Şifre hashleme için context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Bearer token şeması
bearer_scheme = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Şifreyi hashle"""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Şifreyi doğrula"""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(kullanici_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Access token oluştur"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": kullanici_id,
        "exp": expire,
        "type": "access"
    }
    
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)
    return encoded_jwt


def create_refresh_token() -> tuple[str, datetime]:
    """Refresh token oluştur - (token, geçerlilik tarihi) döner"""
    token = str(uuid.uuid4())
    gecerlilik = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    return token, gecerlilik


def decode_token(token: str) -> Optional[dict]:
    """Token'ı decode et"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except JWTError:
        return None


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> Kullanici:
    """
    Mevcut kullanıcıyı al - Dependency Injection için
    JWT token doğrulama ve kullanıcı bilgisi getirme
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "basarili": False,
            "hata": {
                "kod": "YETKISIZ",
                "mesaj": "Geçersiz veya eksik yetkilendirme token'ı."
            }
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    if not credentials:
        raise credentials_exception
    
    token = credentials.credentials
    payload = decode_token(token)
    
    if payload is None:
        raise credentials_exception
    
    kullanici_id = payload.get("sub")
    if kullanici_id is None:
        raise credentials_exception
    
    # Token süresi kontrolü
    exp = payload.get("exp")
    if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "basarili": False,
                "hata": {
                    "kod": "TOKEN_SURESI_DOLDU",
                    "mesaj": "Oturumunuz sona erdi. Lütfen tekrar giriş yapın."
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Kullanıcıyı getir
    result = await db.execute(
        select(Kullanici).where(
            Kullanici.id == kullanici_id,
            Kullanici.silinme_tarihi.is_(None)
        )
    )
    kullanici = result.scalar_one_or_none()
    
    if kullanici is None:
        raise credentials_exception
    
    return kullanici


async def get_current_user_optional(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_db)
) -> Optional[Kullanici]:
    """Opsiyonel kullanıcı - token yoksa None döner"""
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


def require_premium(kullanici: Kullanici = Depends(get_current_user)):
    """Premium üyelik gerektir"""
    if kullanici.abonelik_tipi.value != "PREMIUM":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "basarili": False,
                "hata": {
                    "kod": "PREMIUM_GEREKLI",
                    "mesaj": "Bu özellik sadece Premium üyeler için kullanılabilir."
                }
            }
        )
    return kullanici


def require_verified_email(kullanici: Kullanici = Depends(get_current_user)):
    """E-posta doğrulaması gerektir"""
    if not kullanici.email_dogrulandi:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "basarili": False,
                "hata": {
                    "kod": "EMAIL_DOGRULANMADI",
                    "mesaj": "Lütfen önce e-posta adresinizi doğrulayın."
                }
            }
        )
    return kullanici


def generate_otp(length: int = 6) -> str:
    """OTP kodu oluştur"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])
