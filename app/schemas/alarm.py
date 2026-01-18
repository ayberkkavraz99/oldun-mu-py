"""
Pydantic Şemaları - Alarm ve Bildirimler
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==================== ALARM ====================

class KonumBilgi(BaseModel):
    """Konum bilgisi"""
    enlem: float
    boylam: float


class PanikAlarmRequest(BaseModel):
    """Panik alarm isteği"""
    mesaj: Optional[str] = Field(None, max_length=500)
    konum: Optional[KonumBilgi] = None


class BilgilendirilenKisi(BaseModel):
    """Bilgilendirilen kişi"""
    ad: str
    bildirim_tipi: str  # sms|arama|email


class AlarmBilgi(BaseModel):
    """Alarm bilgisi"""
    id: str
    tarih: datetime
    bilgilendirilen_kisiler: List[BilgilendirilenKisi]


class PanikAlarmResponse(BaseModel):
    """Panik alarm yanıtı"""
    basarili: bool = True
    mesaj: str = "Acil durum alarmı tüm kişilerinize gönderildi."
    alarm: AlarmBilgi


class AlarmIptalRequest(BaseModel):
    """Alarm iptal isteği"""
    alarm_id: str
    iptal_nedeni: Optional[str] = Field(None, max_length=500)


class AlarmGecmisItem(BaseModel):
    """Alarm geçmiş öğesi"""
    id: str
    tip: str  # otomatik|manuel|panik
    tarih: datetime
    durum: str  # aktif|iptal_edildi|cozumlendi
    bilgilendirilen_sayisi: int


class AlarmGecmisResponse(BaseModel):
    """Alarm geçmişi yanıtı"""
    alarmlar: List[AlarmGecmisItem]


# ==================== BİLDİRİM ====================

class SessizSaatler(BaseModel):
    """Sessiz saatler"""
    aktif: bool = True
    baslangic: str = "23:00"
    bitis: str = "07:00"


class BildirimAyarlari(BaseModel):
    """Bildirim ayarları"""
    push_bildirim: bool = True
    email_bildirim: bool = True
    sms_bildirim: bool = True
    hatirlatma_saatleri: List[str] = ["09:00", "21:00"]
    sessiz_saatler: SessizSaatler


class BildirimAyarlariGuncelleRequest(BaseModel):
    """Bildirim ayarları güncelleme"""
    push_bildirim: Optional[bool] = None
    email_bildirim: Optional[bool] = None
    sms_bildirim: Optional[bool] = None
    hatirlatma_saatleri: Optional[List[str]] = None
    sessiz_saatler: Optional[SessizSaatler] = None


class BildirimItem(BaseModel):
    """Bildirim öğesi"""
    id: str
    baslik: str
    icerik: str
    tip: str  # hatirlatma|uyari|alarm|sistem
    okundu: bool
    tarih: datetime


class BildirimListeResponse(BaseModel):
    """Bildirim listesi yanıtı"""
    bildirimler: List[BildirimItem]
