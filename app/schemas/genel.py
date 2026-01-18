"""
Pydantic Şemaları - Genel
"""
from pydantic import BaseModel
from typing import Optional, List


class HataBilgi(BaseModel):
    """Hata bilgisi"""
    kod: str
    mesaj: str
    detay: Optional[str] = None


class HataResponse(BaseModel):
    """Hata yanıtı"""
    basarili: bool = False
    hata: HataBilgi


class BasariliMesajResponse(BaseModel):
    """Genel başarılı mesaj yanıtı"""
    basarili: bool = True
    mesaj: str


class SayfaliSorgu(BaseModel):
    """Sayfalama sorgusu"""
    sayfa: int = 1
    limit: int = 20
