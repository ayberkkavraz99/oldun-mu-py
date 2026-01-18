"""
Pydantic Şemaları - Auth (Kimlik Doğrulama)
"""
from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional
from datetime import datetime
import re


# ==================== REQUEST ŞEMAları ====================

class KayitRequest(BaseModel):
    """Kullanıcı kayıt isteği"""
    ad: str = Field(..., min_length=2, max_length=50, description="Kullanıcı adı")
    soyad: str = Field(..., min_length=2, max_length=50, description="Kullanıcı soyadı")
    email: EmailStr = Field(..., description="E-posta adresi")
    telefon: str = Field(..., description="Telefon numarası")
    sifre: str = Field(..., min_length=8, description="Şifre (en az 8 karakter)")
    sifre_tekrar: str = Field(..., description="Şifre tekrarı")
    dogum_tarihi: Optional[str] = Field(None, description="Doğum tarihi (YYYY-MM-DD)")
    cinsiyet: Optional[str] = Field(None, description="Cinsiyet")
    
    @field_validator('telefon')
    @classmethod
    def validate_telefon(cls, v):
        # Türkiye telefon numarası formatı
        pattern = r'^(\+90|0)?[0-9]{10}$'
        if not re.match(pattern, v.replace(' ', '')):
            raise ValueError('Geçerli bir Türkiye telefon numarası giriniz')
        return v.replace(' ', '')
    
    @field_validator('sifre')
    @classmethod
    def validate_sifre(cls, v):
        if not re.search(r'[a-z]', v):
            raise ValueError('Şifre en az bir küçük harf içermelidir')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Şifre en az bir büyük harf içermelidir')
        if not re.search(r'\d', v):
            raise ValueError('Şifre en az bir rakam içermelidir')
        return v
    
    @field_validator('sifre_tekrar')
    @classmethod
    def validate_sifre_tekrar(cls, v, info):
        if 'sifre' in info.data and v != info.data['sifre']:
            raise ValueError('Şifreler eşleşmiyor')
        return v


class GirisRequest(BaseModel):
    """Kullanıcı giriş isteği"""
    email_veya_telefon: str = Field(..., description="E-posta veya telefon")
    sifre: str = Field(..., description="Şifre")
    cihaz_bilgisi: Optional[dict] = Field(None, description="Cihaz bilgileri")


class RefreshTokenRequest(BaseModel):
    """Token yenileme isteği"""
    refresh_token: str = Field(..., description="Refresh token")


class SifreSifirlamaIstekRequest(BaseModel):
    """Şifre sıfırlama isteği"""
    email: EmailStr = Field(..., description="E-posta adresi")


class SifreSifirlamaDogrulaRequest(BaseModel):
    """Şifre sıfırlama doğrulama"""
    token: str = Field(..., description="Sıfırlama token'ı")
    yeni_sifre: str = Field(..., min_length=8, description="Yeni şifre")
    yeni_sifre_tekrar: str = Field(..., description="Yeni şifre tekrarı")
    
    @field_validator('yeni_sifre_tekrar')
    @classmethod
    def validate_sifre_tekrar(cls, v, info):
        if 'yeni_sifre' in info.data and v != info.data['yeni_sifre']:
            raise ValueError('Şifreler eşleşmiyor')
        return v


class EmailDogrulamaRequest(BaseModel):
    """E-posta doğrulama isteği"""
    dogrulama_kodu: str = Field(..., description="Doğrulama kodu")


class TelefonOTPGonderRequest(BaseModel):
    """Telefon OTP gönderme isteği"""
    telefon: str = Field(..., description="Telefon numarası")


class TelefonOTPOnaylaRequest(BaseModel):
    """Telefon OTP onaylama isteği"""
    telefon: str = Field(..., description="Telefon numarası")
    otp_kodu: str = Field(..., description="OTP kodu")


# ==================== RESPONSE ŞEMAları ====================

class KullaniciBilgi(BaseModel):
    """Basit kullanıcı bilgisi"""
    id: str
    ad: str
    soyad: str
    email: str
    telefon: Optional[str] = None
    
    class Config:
        from_attributes = True


class KayitResponse(BaseModel):
    """Kayıt yanıtı"""
    basarili: bool = True
    mesaj: str
    kullanici: KullaniciBilgi


class GirisKullaniciBilgi(BaseModel):
    """Giriş sonrası kullanıcı bilgisi"""
    id: str
    ad: str
    soyad: str
    email: str
    profil_foto: Optional[str] = None
    abonelik_durumu: str
    son_checkin: Optional[datetime] = None


class GirisResponse(BaseModel):
    """Giriş yanıtı"""
    basarili: bool = True
    access_token: str
    refresh_token: str
    token_suresi: int = 3600
    kullanici: GirisKullaniciBilgi


class TokenYenileResponse(BaseModel):
    """Token yenileme yanıtı"""
    access_token: str
    token_suresi: int = 3600


class BasariliMesajResponse(BaseModel):
    """Genel başarılı mesaj yanıtı"""
    basarili: bool = True
    mesaj: str
