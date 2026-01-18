"""
Check-in Router - Check-in işlemleri
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime, timedelta
from typing import Optional

from app.database import get_db
from app.models import Kullanici, Checkin, RuhHali
from app.schemas.checkin import (
    CheckinRequest, CheckinResponse, CheckinBilgi, IstatistikBilgi,
    CheckinGecmisResponse, CheckinGecmisItem, CheckinKonumDetay,
    CheckinDurumResponse, SonCheckinBilgi, UyariEsikleri,
    CheckinErteleRequest, CheckinErteleResponse
)
from app.utils.security import get_current_user
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/checkin", tags=["Check-in"])


@router.post("", response_model=CheckinResponse)
async def create_checkin(
    request: CheckinRequest,
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check-in yap
    """
    # Check-in oluştur
    checkin = Checkin(
        kullanici_id=kullanici.id,
        tarih=datetime.utcnow(),
        enlem=request.konum.enlem if request.konum else None,
        boylam=request.konum.boylam if request.konum else None,
        not_=request.not_,
        ruh_hali=RuhHali(request.ruh_hali.upper()) if request.ruh_hali else None
    )
    db.add(checkin)
    await db.flush()
    
    # İstatistikleri hesapla
    toplam_checkin = await db.execute(
        select(func.count(Checkin.id)).where(Checkin.kullanici_id == kullanici.id)
    )
    toplam = toplam_checkin.scalar() or 0
    
    # Ardışık gün hesapla
    result = await db.execute(
        select(Checkin.tarih)
        .where(Checkin.kullanici_id == kullanici.id)
        .order_by(Checkin.tarih.desc())
        .limit(100)
    )
    checkinler = result.scalars().all()
    
    ardisik_gun = 0
    if checkinler:
        onceki = datetime.utcnow().date()
        for checkin_tarih in checkinler:
            fark = (onceki - checkin_tarih.date()).days
            if fark <= 1:
                ardisik_gun += 1
                onceki = checkin_tarih.date()
            else:
                break
    
    # Sonraki beklenen check-in
    sonraki_beklenen = datetime.utcnow() + timedelta(hours=kullanici.checkin_suresi_saat)
    
    return CheckinResponse(
        basarili=True,
        mesaj="Check-in başarılı!",
        checkin=CheckinBilgi(
            id=str(checkin.id),
            tarih=checkin.tarih,
            sonraki_checkin_beklenen=sonraki_beklenen,
            kalan_sure_saat=kullanici.checkin_suresi_saat
        ),
        istatistik=IstatistikBilgi(
            ardisik_gun=ardisik_gun,
            toplam_checkin=toplam
        )
    )


@router.get("/gecmis", response_model=CheckinGecmisResponse)
async def get_checkin_history(
    sayfa: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
    baslangic_tarihi: Optional[str] = None,
    bitis_tarihi: Optional[str] = None,
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check-in geçmişi
    """
    # Sorgu oluştur
    query = select(Checkin).where(Checkin.kullanici_id == kullanici.id)
    
    # Tarih filtreleri
    if baslangic_tarihi:
        query = query.where(Checkin.tarih >= datetime.strptime(baslangic_tarihi, "%Y-%m-%d"))
    if bitis_tarihi:
        query = query.where(Checkin.tarih <= datetime.strptime(bitis_tarihi, "%Y-%m-%d"))
    
    # Toplam sayı
    count_query = select(func.count(Checkin.id)).where(Checkin.kullanici_id == kullanici.id)
    if baslangic_tarihi:
        count_query = count_query.where(Checkin.tarih >= datetime.strptime(baslangic_tarihi, "%Y-%m-%d"))
    if bitis_tarihi:
        count_query = count_query.where(Checkin.tarih <= datetime.strptime(bitis_tarihi, "%Y-%m-%d"))
    
    toplam_result = await db.execute(count_query)
    toplam = toplam_result.scalar() or 0
    
    # Sayfalama ve sıralama
    offset = (sayfa - 1) * limit
    query = query.order_by(Checkin.tarih.desc()).offset(offset).limit(limit)
    
    result = await db.execute(query)
    checkinler = result.scalars().all()
    
    return CheckinGecmisResponse(
        toplam=toplam,
        sayfa=sayfa,
        limit=limit,
        checkinler=[
            CheckinGecmisItem(
                id=str(c.id),
                tarih=c.tarih,
                konum=CheckinKonumDetay(
                    enlem=c.enlem,
                    boylam=c.boylam,
                    adres=c.adres
                ) if c.enlem or c.boylam else None,
                not_=c.not_,
                ruh_hali=c.ruh_hali.value.lower() if c.ruh_hali else None
            )
            for c in checkinler
        ]
    )


@router.get("/durum", response_model=CheckinDurumResponse)
async def get_checkin_status(
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check-in durumu
    """
    # Son check-in'i bul
    result = await db.execute(
        select(Checkin)
        .where(Checkin.kullanici_id == kullanici.id)
        .order_by(Checkin.tarih.desc())
        .limit(1)
    )
    son_checkin = result.scalar_one_or_none()
    
    if not son_checkin:
        return CheckinDurumResponse(
            son_checkin=None,
            sonraki_beklenen=None,
            kalan_sure_saat=None,
            durum="alarm",
            uyari_esikleri=UyariEsikleri(
                uyari_saat=20,
                kritik_saat=settings.WARNING_THRESHOLD,
                alarm_saat=settings.ALARM_THRESHOLD
            )
        )
    
    # Süre hesapla
    gecen_sure = datetime.utcnow() - son_checkin.tarih
    gecen_saat = gecen_sure.total_seconds() / 3600
    
    sonraki_beklenen = son_checkin.tarih + timedelta(hours=kullanici.checkin_suresi_saat)
    kalan_sure = (sonraki_beklenen - datetime.utcnow()).total_seconds() / 3600
    
    # Durum belirleme
    if gecen_saat < 20:
        durum = "guvenli"
    elif gecen_saat < settings.WARNING_THRESHOLD:
        durum = "uyari"
    elif gecen_saat < settings.ALARM_THRESHOLD:
        durum = "kritik"
    else:
        durum = "alarm"
    
    return CheckinDurumResponse(
        son_checkin=SonCheckinBilgi(
            tarih=son_checkin.tarih,
            gecen_sure_saat=round(gecen_saat, 1)
        ),
        sonraki_beklenen=sonraki_beklenen,
        kalan_sure_saat=round(max(0, kalan_sure), 1),
        durum=durum,
        uyari_esikleri=UyariEsikleri(
            uyari_saat=20,
            kritik_saat=settings.WARNING_THRESHOLD,
            alarm_saat=settings.ALARM_THRESHOLD
        )
    )


@router.post("/ertele", response_model=CheckinErteleResponse)
async def postpone_checkin(
    request: CheckinErteleRequest,
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check-in hatırlatma ertele
    """
    # Son check-in'i bul
    result = await db.execute(
        select(Checkin)
        .where(Checkin.kullanici_id == kullanici.id)
        .order_by(Checkin.tarih.desc())
        .limit(1)
    )
    son_checkin = result.scalar_one_or_none()
    
    if not son_checkin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"basarili": False, "hata": {"kod": "CHECKIN_YOK", "mesaj": "Henüz check-in yapmadınız."}}
        )
    
    # Yeni beklenen tarihi hesapla
    yeni_beklenen = son_checkin.tarih + timedelta(
        hours=kullanici.checkin_suresi_saat + request.ek_sure_saat
    )
    
    return CheckinErteleResponse(
        basarili=True,
        yeni_beklenen_tarih=yeni_beklenen
    )
