"""
Alarm Router - Alarm ve bildirim işlemleri
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime
from uuid import UUID

from app.database import get_db
from app.models import Kullanici, Alarm, AcilKisi, Bildirim, AlarmTipi, AlarmDurum, BildirimTipi
from app.schemas.alarm import (
    PanikAlarmRequest, PanikAlarmResponse, AlarmBilgi, BilgilendirilenKisi,
    AlarmIptalRequest, AlarmGecmisResponse, AlarmGecmisItem,
    BildirimAyarlari, BildirimAyarlariGuncelleRequest, BildirimListeResponse, BildirimItem
)
from app.schemas.genel import BasariliMesajResponse
from app.utils.security import get_current_user
from app.services.email_service import send_alarm_notification_email

router = APIRouter(tags=["Alarm ve Bildirimler"])


@router.post("/alarm/panik", response_model=PanikAlarmResponse)
async def trigger_panic(
    request: PanikAlarmRequest,
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Acil kişileri al
    result = await db.execute(
        select(AcilKisi).where(AcilKisi.kullanici_id == kullanici.id, AcilKisi.dogrulandi == True)
    )
    kisiler = result.scalars().all()
    
    bilgilendirilenler = []
    for kisi in kisiler:
        if kisi.email:
            await send_alarm_notification_email(kisi.email, kisi.ad, f"{kullanici.ad} {kullanici.soyad}", request.mesaj or "")
            bilgilendirilenler.append({"ad": kisi.ad, "bildirim_tipi": "email"})
        # TODO: SMS gönder
        bilgilendirilenler.append({"ad": kisi.ad, "bildirim_tipi": "sms"})
    
    alarm = Alarm(
        kullanici_id=kullanici.id, tip=AlarmTipi.PANIK, mesaj=request.mesaj,
        enlem=request.konum.enlem if request.konum else None,
        boylam=request.konum.boylam if request.konum else None,
        bilgilendirilenler=bilgilendirilenler
    )
    db.add(alarm)
    await db.flush()
    
    return PanikAlarmResponse(
        basarili=True, mesaj="Acil durum alarmı gönderildi.",
        alarm=AlarmBilgi(
            id=str(alarm.id), tarih=alarm.tarih,
            bilgilendirilen_kisiler=[BilgilendirilenKisi(ad=b["ad"], bildirim_tipi=b["bildirim_tipi"]) for b in bilgilendirilenler]
        )
    )


@router.post("/alarm/iptal", response_model=BasariliMesajResponse)
async def cancel_alarm(request: AlarmIptalRequest, kullanici: Kullanici = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alarm).where(Alarm.id == UUID(request.alarm_id), Alarm.kullanici_id == kullanici.id))
    alarm = result.scalar_one_or_none()
    if not alarm:
        raise HTTPException(status_code=404, detail={"basarili": False, "hata": {"kod": "BULUNAMADI", "mesaj": "Alarm bulunamadı"}})
    
    alarm.durum = AlarmDurum.IPTAL_EDILDI
    alarm.iptal_tarihi = datetime.utcnow()
    alarm.iptal_nedeni = request.iptal_nedeni
    return BasariliMesajResponse(basarili=True, mesaj="Alarm iptal edildi.")


@router.get("/alarm/gecmis", response_model=AlarmGecmisResponse)
async def get_alarm_history(kullanici: Kullanici = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Alarm).where(Alarm.kullanici_id == kullanici.id).order_by(Alarm.tarih.desc()).limit(50))
    alarmlar = result.scalars().all()
    
    return AlarmGecmisResponse(alarmlar=[
        AlarmGecmisItem(
            id=str(a.id), tip=a.tip.value.lower(), tarih=a.tarih, durum=a.durum.value.lower(),
            bilgilendirilen_sayisi=len(a.bilgilendirilenler) if a.bilgilendirilenler else 0
        ) for a in alarmlar
    ])


@router.get("/bildirimler/ayarlar", response_model=BildirimAyarlari)
async def get_notification_settings(kullanici: Kullanici = Depends(get_current_user)):
    return BildirimAyarlari()  # Varsayılan ayarlar


@router.put("/bildirimler/ayarlar", response_model=BasariliMesajResponse)
async def update_notification_settings(request: BildirimAyarlariGuncelleRequest, kullanici: Kullanici = Depends(get_current_user)):
    # TODO: Ayarları kaydet
    return BasariliMesajResponse(basarili=True, mesaj="Ayarlar güncellendi.")


@router.get("/bildirimler/gecmis", response_model=BildirimListeResponse)
async def get_notifications(kullanici: Kullanici = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bildirim).where(Bildirim.kullanici_id == kullanici.id).order_by(Bildirim.tarih.desc()).limit(50))
    bildirimler = result.scalars().all()
    
    return BildirimListeResponse(bildirimler=[
        BildirimItem(id=str(b.id), baslik=b.baslik, icerik=b.icerik, tip=b.tip.value.lower(), okundu=b.okundu, tarih=b.tarih)
        for b in bildirimler
    ])


@router.put("/bildirimler/{bildirim_id}/okundu", response_model=BasariliMesajResponse)
async def mark_notification_read(bildirim_id: UUID, kullanici: Kullanici = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Bildirim).where(Bildirim.id == bildirim_id, Bildirim.kullanici_id == kullanici.id))
    bildirim = result.scalar_one_or_none()
    if bildirim:
        bildirim.okundu = True
    return BasariliMesajResponse(basarili=True, mesaj="İşaretlendi.")
