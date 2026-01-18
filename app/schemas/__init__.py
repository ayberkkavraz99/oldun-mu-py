"""Schemas package"""
from app.schemas.auth import (
    KayitRequest,
    GirisRequest,
    RefreshTokenRequest,
    SifreSifirlamaIstekRequest,
    SifreSifirlamaDogrulaRequest,
    EmailDogrulamaRequest,
    TelefonOTPGonderRequest,
    TelefonOTPOnaylaRequest,
    KayitResponse,
    GirisResponse,
    TokenYenileResponse,
)

from app.schemas.kullanici import (
    ProfilResponse,
    ProfilGuncelleRequest,
    SifreDegistirRequest,
    HesapSilRequest,
    ProfilFotoResponse,
)

from app.schemas.checkin import (
    CheckinRequest,
    CheckinResponse,
    CheckinGecmisResponse,
    CheckinDurumResponse,
    CheckinErteleRequest,
    CheckinErteleResponse,
)

from app.schemas.acil_kisi import (
    AcilKisiEkleRequest,
    AcilKisiGuncelleRequest,
    AcilKisiListeResponse,
    AcilKisiEkleResponse,
)

from app.schemas.alarm import (
    PanikAlarmRequest,
    PanikAlarmResponse,
    AlarmIptalRequest,
    AlarmGecmisResponse,
    BildirimAyarlari,
    BildirimAyarlariGuncelleRequest,
    BildirimListeResponse,
)

from app.schemas.genel import (
    HataResponse,
    BasariliMesajResponse,
    SayfaliSorgu,
)

__all__ = [
    # Auth
    "KayitRequest",
    "GirisRequest",
    "RefreshTokenRequest",
    "KayitResponse",
    "GirisResponse",
    "TokenYenileResponse",
    # Kullanici
    "ProfilResponse",
    "ProfilGuncelleRequest",
    # Checkin
    "CheckinRequest",
    "CheckinResponse",
    # Acil Kisi
    "AcilKisiEkleRequest",
    "AcilKisiListeResponse",
    # Alarm
    "PanikAlarmRequest",
    "PanikAlarmResponse",
    # Genel
    "HataResponse",
    "BasariliMesajResponse",
]
