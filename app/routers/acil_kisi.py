"""
Acil Kişi Router - Acil durum kişileri yönetimi
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from uuid import UUID

from app.database import get_db
from app.models import Kullanici, AcilKisi, Iliski, AbonelikTipi
from app.schemas.acil_kisi import (
    AcilKisiEkleRequest, AcilKisiGuncelleRequest,
    AcilKisiListeResponse, AcilKisiEkleResponse, AcilKisiBilgi
)
from app.schemas.genel import BasariliMesajResponse
from app.utils.security import get_current_user, generate_otp
from app.config import SUBSCRIPTION_PLANS

router = APIRouter(prefix="/acil-kisiler", tags=["Acil Durum Kişileri"])


def get_max_acil_kisi(abonelik_tipi: AbonelikTipi) -> int:
    for plan in SUBSCRIPTION_PLANS:
        if plan["id"] == "ucretsiz" and abonelik_tipi == AbonelikTipi.UCRETSIZ:
            return plan["max_acil_kisi"]
        elif plan["id"] == "aylik_premium" and abonelik_tipi == AbonelikTipi.PREMIUM:
            return plan["max_acil_kisi"]
    return 2


@router.get("", response_model=AcilKisiListeResponse)
async def list_acil_kisiler(
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(AcilKisi).where(AcilKisi.kullanici_id == kullanici.id).order_by(AcilKisi.oncelik)
    )
    kisiler = result.scalars().all()
    max_kisi = get_max_acil_kisi(kullanici.abonelik_tipi)
    
    return AcilKisiListeResponse(
        kisiler=[AcilKisiBilgi(
            id=str(k.id), ad=k.ad, soyad=k.soyad, telefon=k.telefon, email=k.email,
            iliski=k.iliski.value.lower(), oncelik=k.oncelik, dogrulandi=k.dogrulandi,
            ekleme_tarihi=k.ekleme_tarihi
        ) for k in kisiler],
        maksimum_kisi_sayisi=max_kisi, mevcut_sayi=len(kisiler)
    )


@router.post("", response_model=AcilKisiEkleResponse, status_code=status.HTTP_201_CREATED)
async def add_acil_kisi(
    request: AcilKisiEkleRequest,
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(func.count(AcilKisi.id)).where(AcilKisi.kullanici_id == kullanici.id)
    )
    mevcut_sayi = result.scalar() or 0
    max_kisi = get_max_acil_kisi(kullanici.abonelik_tipi)
    
    if mevcut_sayi >= max_kisi:
        raise HTTPException(status_code=400, detail={"basarili": False, "hata": {"kod": "LIMIT", "mesaj": "Limit aşıldı"}})
    
    telefon = request.telefon.replace(" ", "")
    if telefon.startswith("0"): telefon = "+90" + telefon[1:]
    elif not telefon.startswith("+"): telefon = "+90" + telefon
    
    acil_kisi = AcilKisi(
        kullanici_id=kullanici.id, ad=request.ad, soyad=request.soyad, telefon=telefon,
        email=request.email, iliski=Iliski(request.iliski.upper()) if request.iliski else Iliski.DIGER,
        oncelik=request.oncelik or 1, ozel_mesaj=request.ozel_mesaj, dogrulama_kodu=generate_otp()
    )
    db.add(acil_kisi)
    await db.flush()
    
    return AcilKisiEkleResponse(
        basarili=True, mesaj="Acil durum kişisi eklendi.",
        kisi=AcilKisiBilgi(
            id=str(acil_kisi.id), ad=acil_kisi.ad, soyad=acil_kisi.soyad, telefon=acil_kisi.telefon,
            email=acil_kisi.email, iliski=acil_kisi.iliski.value.lower(), oncelik=acil_kisi.oncelik,
            dogrulandi=acil_kisi.dogrulandi, ekleme_tarihi=acil_kisi.ekleme_tarihi
        )
    )


@router.put("/{kisi_id}", response_model=BasariliMesajResponse)
async def update_acil_kisi(kisi_id: UUID, request: AcilKisiGuncelleRequest,
    kullanici: Kullanici = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AcilKisi).where(AcilKisi.id == kisi_id, AcilKisi.kullanici_id == kullanici.id))
    acil_kisi = result.scalar_one_or_none()
    if not acil_kisi:
        raise HTTPException(status_code=404, detail={"basarili": False, "hata": {"kod": "BULUNAMADI", "mesaj": "Bulunamadı"}})
    
    if request.ad: acil_kisi.ad = request.ad
    if request.soyad: acil_kisi.soyad = request.soyad
    if request.email: acil_kisi.email = request.email
    if request.oncelik: acil_kisi.oncelik = request.oncelik
    
    return BasariliMesajResponse(basarili=True, mesaj="Güncellendi.")


@router.delete("/{kisi_id}", response_model=BasariliMesajResponse)
async def delete_acil_kisi(kisi_id: UUID, kullanici: Kullanici = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(AcilKisi).where(AcilKisi.id == kisi_id, AcilKisi.kullanici_id == kullanici.id))
    acil_kisi = result.scalar_one_or_none()
    if not acil_kisi:
        raise HTTPException(status_code=404, detail={"basarili": False, "hata": {"kod": "BULUNAMADI", "mesaj": "Bulunamadı"}})
    await db.delete(acil_kisi)
    return BasariliMesajResponse(basarili=True, mesaj="Silindi.")
