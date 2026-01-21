"""
Auth Router - Supabase Users Tablosu ile Kimlik Doğrulama
"""
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re

from app.database import get_supabase
from app.utils.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Kimlik Doğrulama"])


# ==================== REQUEST ŞEMAları ====================

class RegisterRequest(BaseModel):
    """Kullanıcı kayıt isteği"""
    email: EmailStr = Field(..., description="E-posta adresi")
    password: str = Field(..., min_length=8, description="Şifre (en az 8 karakter)")
    first_name: Optional[str] = Field(None, max_length=100, description="Ad")
    last_name: Optional[str] = Field(None, max_length=100, description="Soyad")
    phone_number: Optional[str] = Field(None, max_length=20, description="Telefon numarası")
    
    @field_validator('password')
    @classmethod
    def validate_password(cls, v):
        if not re.search(r'[a-z]', v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'\d', v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        return v


class LoginRequest(BaseModel):
    """Kullanıcı giriş isteği"""
    email: EmailStr = Field(..., description="E-posta adresi")
    password: str = Field(..., description="Şifre")


# ==================== RESPONSE ŞEMAları ====================

class UserInfo(BaseModel):
    """Kullanıcı bilgisi"""
    id: str
    email: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone_number: Optional[str] = None
    is_active: bool = True
    is_verified: bool = False
    role: str = "user"


class RegisterResponse(BaseModel):
    """Kayıt yanıtı"""
    success: bool = True
    message: str
    user: UserInfo


class LoginResponse(BaseModel):
    """Giriş yanıtı"""
    success: bool = True
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    user: UserInfo


class MessageResponse(BaseModel):
    """Genel mesaj yanıtı"""
    success: bool = True
    message: str


# ==================== ENDPOINTS ====================

@router.post("/register", response_model=RegisterResponse, status_code=status.HTTP_201_CREATED)
async def register(request: RegisterRequest):
    """
    Yeni kullanıcı kaydı - Supabase users tablosuna kayıt yapar
    """
    supabase = get_supabase()
    
    # E-posta kontrolü
    existing = supabase.table("users").select("id").eq("email", request.email).execute()
    
    if existing.data and len(existing.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "error": {"code": "EMAIL_EXISTS", "message": "Bu e-posta adresi zaten kayıtlı."}}
        )
    
    # Şifreyi hashle
    password_hash = hash_password(request.password)
    
    # Kullanıcı verisini hazırla
    user_data = {
        "email": request.email,
        "password_hash": password_hash,
        "first_name": request.first_name,
        "last_name": request.last_name,
        "phone_number": request.phone_number,
        "is_active": True,
        "is_verified": False,
        "role": "user"
    }
    
    # Supabase'e kaydet
    result = supabase.table("users").insert(user_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "error": {"code": "INSERT_FAILED", "message": "Kullanıcı kaydedilemedi."}}
        )
    
    user = result.data[0]
    
    return RegisterResponse(
        success=True,
        message="Kayıt başarılı!",
        user=UserInfo(
            id=user["id"],
            email=user["email"],
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            phone_number=user.get("phone_number"),
            is_active=user.get("is_active", True),
            is_verified=user.get("is_verified", False),
            role=user.get("role", "user")
        )
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """
    Kullanıcı girişi
    """
    supabase = get_supabase()
    
    # Kullanıcıyı bul
    result = supabase.table("users").select("*").eq("email", request.email).execute()
    
    if not result.data or len(result.data) == 0:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error": {"code": "INVALID_CREDENTIALS", "message": "E-posta veya şifre hatalı."}}
        )
    
    user = result.data[0]
    
    # Şifre kontrolü
    if not verify_password(request.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"success": False, "error": {"code": "INVALID_CREDENTIALS", "message": "E-posta veya şifre hatalı."}}
        )
    
    # Aktif mi kontrolü
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"success": False, "error": {"code": "ACCOUNT_INACTIVE", "message": "Hesabınız devre dışı."}}
        )
    
    # Access token oluştur
    access_token = create_access_token(user["id"])
    
    # Son giriş zamanını güncelle
    supabase.table("users").update({"last_login_at": datetime.utcnow().isoformat()}).eq("id", user["id"]).execute()
    
    return LoginResponse(
        success=True,
        access_token=access_token,
        token_type="bearer",
        expires_in=3600,
        user=UserInfo(
            id=user["id"],
            email=user["email"],
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            phone_number=user.get("phone_number"),
            is_active=user.get("is_active", True),
            is_verified=user.get("is_verified", False),
            role=user.get("role", "user")
        )
    )


@router.get("/me", response_model=UserInfo)
async def get_current_user_info():
    """
    Mevcut kullanıcı bilgilerini getir (TODO: JWT auth eklenecek)
    """
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail={"success": False, "error": {"code": "NOT_IMPLEMENTED", "message": "Bu endpoint henüz implement edilmedi."}}
    )
