"""
Pydantic Şemaları - Acil Durum Kişileri
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class AcilKisiEkleRequest(BaseModel):
    """Acil kişi ekleme isteği"""
    ad: str = Field(..., min_length=2, max_length=50)
    soyad: str = Field(..., min_length=2, max_length=50)
    telefon: str = Field(..., description="Telefon numarası")
    email: Optional[EmailStr] = None
    iliski: Optional[str] = Field("diger", description="aile|arkadas|komsu|diger")
    oncelik: Optional[int] = Field(1, ge=1, le=5)
    ozel_mesaj: Optional[str] = Field(None, max_length=500)


class AcilKisiGuncelleRequest(BaseModel):
    """Acil kişi güncelleme isteği"""
    ad: Optional[str] = Field(None, min_length=2, max_length=50)
    soyad: Optional[str] = Field(None, min_length=2, max_length=50)
    telefon: Optional[str] = None
    email: Optional[EmailStr] = None
    iliski: Optional[str] = None
    oncelik: Optional[int] = Field(None, ge=1, le=5)
    ozel_mesaj: Optional[str] = Field(None, max_length=500)


class AcilKisiBilgi(BaseModel):
    """Acil kişi bilgisi"""
    id: str
    ad: str
    soyad: str
    telefon: str
    email: Optional[str] = None
    iliski: str
    oncelik: int
    dogrulandi: bool
    ekleme_tarihi: datetime
    
    class Config:
        from_attributes = True


class AcilKisiListeResponse(BaseModel):
    """Acil kişi listesi yanıtı"""
    kisiler: List[AcilKisiBilgi]
    maksimum_kisi_sayisi: int = 5
    mevcut_sayi: int


class AcilKisiEkleResponse(BaseModel):
    """Acil kişi ekleme yanıtı"""
    basarili: bool = True
    mesaj: str = "Acil durum kişisi eklendi. Doğrulama SMS'i gönderildi."
    kisi: AcilKisiBilgi
