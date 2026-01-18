"""
Pydantic Şemaları - Check-in
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class KonumBilgi(BaseModel):
    """Konum bilgisi"""
    enlem: float = Field(..., ge=-90, le=90)
    boylam: float = Field(..., ge=-180, le=180)


class CheckinRequest(BaseModel):
    """Check-in isteği"""
    konum: Optional[KonumBilgi] = None
    not_: Optional[str] = Field(None, max_length=500, alias="not")
    ruh_hali: Optional[str] = Field(None, description="iyi|orta|kotu")
    
    class Config:
        populate_by_name = True


class CheckinBilgi(BaseModel):
    """Check-in bilgisi"""
    id: str
    tarih: datetime
    sonraki_checkin_beklenen: datetime
    kalan_sure_saat: int


class IstatistikBilgi(BaseModel):
    """Check-in istatistikleri"""
    ardisik_gun: int
    toplam_checkin: int


class CheckinResponse(BaseModel):
    """Check-in yanıtı"""
    basarili: bool = True
    mesaj: str = "Check-in başarılı!"
    checkin: CheckinBilgi
    istatistik: IstatistikBilgi


class CheckinKonumDetay(BaseModel):
    """Check-in konum detayı"""
    enlem: Optional[float] = None
    boylam: Optional[float] = None
    adres: Optional[str] = None


class CheckinGecmisItem(BaseModel):
    """Check-in geçmiş öğesi"""
    id: str
    tarih: datetime
    konum: Optional[CheckinKonumDetay] = None
    not_: Optional[str] = Field(None, alias="not")
    ruh_hali: Optional[str] = None
    
    class Config:
        populate_by_name = True


class CheckinGecmisResponse(BaseModel):
    """Check-in geçmişi yanıtı"""
    toplam: int
    sayfa: int
    limit: int
    checkinler: List[CheckinGecmisItem]


class UyariEsikleri(BaseModel):
    """Uyarı eşikleri"""
    uyari_saat: int = 20
    kritik_saat: int = 44
    alarm_saat: int = 48


class SonCheckinBilgi(BaseModel):
    """Son check-in bilgisi"""
    tarih: datetime
    gecen_sure_saat: float


class CheckinDurumResponse(BaseModel):
    """Check-in durumu yanıtı"""
    son_checkin: Optional[SonCheckinBilgi] = None
    sonraki_beklenen: Optional[datetime] = None
    kalan_sure_saat: Optional[float] = None
    durum: str = Field(..., description="guvenli|uyari|kritik|alarm")
    uyari_esikleri: UyariEsikleri


class CheckinErteleRequest(BaseModel):
    """Check-in erteleme isteği"""
    ek_sure_saat: int = Field(..., ge=1, le=24, description="1-24 saat")


class CheckinErteleResponse(BaseModel):
    """Check-in erteleme yanıtı"""
    basarili: bool = True
    yeni_beklenen_tarih: datetime
