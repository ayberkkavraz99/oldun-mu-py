"""
Güvenlik yardımcı fonksiyonları - JWT, şifre hashleme vb. (Supabase uyumlu)
"""
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uuid

from app.config import get_settings

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


def create_access_token(user_id: str, expires_delta: Optional[timedelta] = None) -> str:
    """Access token oluştur"""
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode = {
        "sub": user_id,
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


def get_user_id_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme)
) -> str:
    """
    Token'dan kullanıcı ID'sini al
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "success": False,
            "error": {
                "code": "UNAUTHORIZED",
                "message": "Geçersiz veya eksik yetkilendirme token'ı."
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
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    # Token süresi kontrolü
    exp = payload.get("exp")
    if exp and datetime.utcfromtimestamp(exp) < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "success": False,
                "error": {
                    "code": "TOKEN_EXPIRED",
                    "message": "Oturumunuz sona erdi. Lütfen tekrar giriş yapın."
                }
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return user_id


def generate_otp(length: int = 6) -> str:
    """OTP kodu oluştur"""
    import random
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])
