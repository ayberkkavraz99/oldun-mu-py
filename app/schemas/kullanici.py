"""
Pydantic Şemaları - Kullanıcı
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class AdresBilgi(BaseModel):
    """Adres bilgisi"""
    il: Optional[str] = None
    ilce: Optional[str] = None
    tam_adres: Optional[str] = None


class AbonelikBilgi(BaseModel):
    """Abonelik bilgisi"""
    tip: str
    bitis_tarihi: Optional[datetime] = None
    otomatik_yenileme: bool = True


class AyarlarBilgi(BaseModel):
    """Kullanıcı ayarları"""
    checkin_suresi_saat: int = 24
    bildirim_aktif: bool = True
    ses_aktif: bool = True
    titresim_aktif: bool = True


class IstatistikBilgi(BaseModel):
    """Kullanıcı istatistikleri"""
    toplam_checkin: int = 0
    ardisik_gun: int = 0
    kayit_tarihi: datetime


class ProfilResponse(BaseModel):
    """Profil bilgileri yanıtı"""
    id: str
    ad: str
    soyad: str
    email: str
    telefon: str
    profil_foto: Optional[str] = None
    dogum_tarihi: Optional[datetime] = None
    cinsiyet: Optional[str] = None
    adres: Optional[AdresBilgi] = None
    abonelik: AbonelikBilgi
    ayarlar: AyarlarBilgi
    istatistikler: IstatistikBilgi


class ProfilGuncelleRequest(BaseModel):
    """Profil güncelleme isteği"""
    ad: Optional[str] = Field(None, min_length=2, max_length=50)
    soyad: Optional[str] = Field(None, min_length=2, max_length=50)
    dogum_tarihi: Optional[str] = None
    cinsiyet: Optional[str] = None
    adres: Optional[AdresBilgi] = None


class SifreDegistirRequest(BaseModel):
    """Şifre değiştirme isteği"""
    mevcut_sifre: str = Field(..., description="Mevcut şifre")
    yeni_sifre: str = Field(..., min_length=8, description="Yeni şifre")
    yeni_sifre_tekrar: str = Field(..., description="Yeni şifre tekrarı")


class HesapSilRequest(BaseModel):
    """Hesap silme isteği"""
    sifre: str = Field(..., description="Şifre onayı")
    silme_nedeni: Optional[str] = Field(None, description="Silme nedeni")


class ProfilFotoResponse(BaseModel):
    """Profil fotoğrafı yanıtı"""
    basarili: bool = True
    profil_foto_url: str
