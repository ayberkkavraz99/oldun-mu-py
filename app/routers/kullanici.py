"""
Kullanıcı Router - Profil yönetimi endpoint'leri
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from datetime import datetime
import os
import uuid
import aiofiles

from app.database import get_db
from app.models import Kullanici, Checkin, RefreshToken
from app.schemas.kullanici import (
    ProfilResponse, ProfilGuncelleRequest, SifreDegistirRequest,
    HesapSilRequest, ProfilFotoResponse, AbonelikBilgi, AyarlarBilgi, IstatistikBilgi
)
from app.schemas.genel import BasariliMesajResponse
from app.utils.security import get_current_user, hash_password, verify_password
from app.config import get_settings

settings = get_settings()
router = APIRouter(prefix="/kullanici", tags=["Kullanıcı"])


@router.get("/profil", response_model=ProfilResponse)
async def get_profile(
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Profil bilgilerini getir
    """
    # Toplam check-in sayısı
    result = await db.execute(
        select(func.count(Checkin.id)).where(Checkin.kullanici_id == kullanici.id)
    )
    toplam_checkin = result.scalar() or 0
    
    # Ardışık gün hesapla (basitleştirilmiş)
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
    
    return ProfilResponse(
        id=str(kullanici.id),
        ad=kullanici.ad,
        soyad=kullanici.soyad,
        email=kullanici.email,
        telefon=kullanici.telefon,
        profil_foto=kullanici.profil_foto,
        dogum_tarihi=kullanici.dogum_tarihi,
        cinsiyet=kullanici.cinsiyet.value.lower() if kullanici.cinsiyet else None,
        adres=kullanici.adres,
        abonelik=AbonelikBilgi(
            tip=kullanici.abonelik_tipi.value.lower(),
            bitis_tarihi=kullanici.abonelik_bitis,
            otomatik_yenileme=True
        ),
        ayarlar=AyarlarBilgi(
            checkin_suresi_saat=kullanici.checkin_suresi_saat,
            bildirim_aktif=True,
            ses_aktif=True,
            titresim_aktif=True
        ),
        istatistikler=IstatistikBilgi(
            toplam_checkin=toplam_checkin,
            ardisik_gun=ardisik_gun,
            kayit_tarihi=kullanici.olusturma_tarihi
        )
    )


@router.put("/profil", response_model=BasariliMesajResponse)
async def update_profile(
    request: ProfilGuncelleRequest,
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Profil güncelle
    """
    if request.ad:
        kullanici.ad = request.ad
    if request.soyad:
        kullanici.soyad = request.soyad
    if request.dogum_tarihi:
        kullanici.dogum_tarihi = datetime.strptime(request.dogum_tarihi, "%Y-%m-%d")
    if request.cinsiyet:
        kullanici.cinsiyet = request.cinsiyet.upper()
    if request.adres:
        kullanici.adres = request.adres.model_dump()
    
    return BasariliMesajResponse(basarili=True, mesaj="Profil başarıyla güncellendi.")


@router.post("/profil-foto", response_model=ProfilFotoResponse)
async def upload_profile_photo(
    foto: UploadFile = File(...),
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Profil fotoğrafı yükle
    """
    # Dosya türü kontrolü
    allowed_types = ["image/jpeg", "image/png", "image/webp"]
    if foto.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"basarili": False, "hata": {"kod": "GECERSIZ_DOSYA", "mesaj": "Sadece JPEG, PNG ve WebP dosyaları kabul edilir."}}
        )
    
    # Dosya boyutu kontrolü
    content = await foto.read()
    if len(content) > settings.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"basarili": False, "hata": {"kod": "DOSYA_COK_BUYUK", "mesaj": "Dosya boyutu 5MB'dan büyük olamaz."}}
        )
    
    # Dosyayı kaydet
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_ext = foto.filename.split(".")[-1] if foto.filename else "jpg"
    file_name = f"{uuid.uuid4()}.{file_ext}"
    file_path = os.path.join(settings.UPLOAD_DIR, file_name)
    
    async with aiofiles.open(file_path, "wb") as f:
        await f.write(content)
    
    # URL oluştur ve kaydet
    foto_url = f"/uploads/{file_name}"
    kullanici.profil_foto = foto_url
    
    return ProfilFotoResponse(basarili=True, profil_foto_url=foto_url)


@router.put("/sifre-degistir", response_model=BasariliMesajResponse)
async def change_password(
    request: SifreDegistirRequest,
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Şifre değiştir
    """
    # Mevcut şifre kontrolü
    if not verify_password(request.mevcut_sifre, kullanici.sifre_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"basarili": False, "hata": {"kod": "YANLIS_SIFRE", "mesaj": "Mevcut şifre hatalı."}}
        )
    
    # Şifre eşleşme kontrolü
    if request.yeni_sifre != request.yeni_sifre_tekrar:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"basarili": False, "hata": {"kod": "SIFRE_ESLESMIYOR", "mesaj": "Şifreler eşleşmiyor."}}
        )
    
    # Yeni şifreyi kaydet
    kullanici.sifre_hash = hash_password(request.yeni_sifre)
    
    # Diğer oturumları sonlandır
    await db.execute(
        RefreshToken.__table__.update()
        .where(RefreshToken.kullanici_id == kullanici.id)
        .values(iptal_edildi=True)
    )
    
    return BasariliMesajResponse(basarili=True, mesaj="Şifreniz başarıyla değiştirildi.")


@router.delete("/hesap", response_model=BasariliMesajResponse)
async def delete_account(
    request: HesapSilRequest,
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Hesabı sil (soft delete - 30 gün sonra kalıcı)
    """
    # Şifre kontrolü
    if not verify_password(request.sifre, kullanici.sifre_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"basarili": False, "hata": {"kod": "YANLIS_SIFRE", "mesaj": "Şifre hatalı."}}
        )
    
    # Soft delete - 30 gün sonra kalıcı silinecek
    from datetime import timedelta
    kullanici.silinme_tarihi = datetime.utcnow() + timedelta(days=30)
    
    # Tüm oturumları sonlandır
    await db.execute(
        RefreshToken.__table__.update()
        .where(RefreshToken.kullanici_id == kullanici.id)
        .values(iptal_edildi=True)
    )
    
    return BasariliMesajResponse(
        basarili=True,
        mesaj="Hesabınız 30 gün içinde kalıcı olarak silinecektir."
    )
