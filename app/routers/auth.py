"""
Auth Router - Kimlik doğrulama endpoint'leri
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from datetime import datetime, timedelta
import uuid

from app.database import get_db
from app.models import Kullanici, RefreshToken, DogrulamaKodu, Checkin, DogrulamaTipi
from app.schemas.auth import (
    KayitRequest, KayitResponse, KullaniciBilgi,
    GirisRequest, GirisResponse, GirisKullaniciBilgi,
    RefreshTokenRequest, TokenYenileResponse,
    SifreSifirlamaIstekRequest, SifreSifirlamaDogrulaRequest,
    EmailDogrulamaRequest, TelefonOTPGonderRequest, TelefonOTPOnaylaRequest,
    BasariliMesajResponse
)
from app.utils.security import (
    hash_password, verify_password, 
    create_access_token, create_refresh_token,
    get_current_user, generate_otp
)
from app.services.email_service import send_verification_email, send_password_reset_email

router = APIRouter(prefix="/auth", tags=["Kimlik Doğrulama"])


@router.post("/register", response_model=KayitResponse, status_code=status.HTTP_201_CREATED)
async def register(request: KayitRequest, db: AsyncSession = Depends(get_db)):
    """
    Yeni kullanıcı kaydı
    """
    # E-posta kontrolü
    result = await db.execute(select(Kullanici).where(Kullanici.email == request.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"basarili": False, "hata": {"kod": "EMAIL_MEVCUT", "mesaj": "Bu e-posta adresi zaten kayıtlı."}}
        )
    
    # Telefon kontrolü
    telefon_normalized = request.telefon.replace(" ", "")
    if telefon_normalized.startswith("0"):
        telefon_normalized = "+90" + telefon_normalized[1:]
    elif not telefon_normalized.startswith("+"):
        telefon_normalized = "+90" + telefon_normalized
    
    result = await db.execute(
        select(Kullanici).where(Kullanici.telefon.contains(request.telefon[-10:]))
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"basarili": False, "hata": {"kod": "TELEFON_MEVCUT", "mesaj": "Bu telefon numarası zaten kayıtlı."}}
        )
    
    # Kullanıcı oluştur
    kullanici = Kullanici(
        email=request.email,
        telefon=telefon_normalized,
        sifre_hash=hash_password(request.sifre),
        ad=request.ad,
        soyad=request.soyad,
        dogum_tarihi=datetime.strptime(request.dogum_tarihi, "%Y-%m-%d") if request.dogum_tarihi else None,
        cinsiyet=request.cinsiyet.upper() if request.cinsiyet else None,
    )
    
    db.add(kullanici)
    await db.flush()
    
    # E-posta doğrulama kodu oluştur
    dogrulama_kodu = generate_otp()
    kod = DogrulamaKodu(
        kullanici_id=kullanici.id,
        kod=dogrulama_kodu,
        tip=DogrulamaTipi.EMAIL,
        gecerlilik=datetime.utcnow() + timedelta(hours=24)
    )
    db.add(kod)
    
    # E-posta gönder
    await send_verification_email(request.email, request.ad, dogrulama_kodu)
    
    return KayitResponse(
        basarili=True,
        mesaj="Kayıt başarılı. Lütfen e-postanızı doğrulayın.",
        kullanici=KullaniciBilgi(
            id=str(kullanici.id),
            ad=kullanici.ad,
            soyad=kullanici.soyad,
            email=kullanici.email,
            telefon=kullanici.telefon
        )
    )


@router.post("/login", response_model=GirisResponse)
async def login(request: GirisRequest, db: AsyncSession = Depends(get_db)):
    """
    Kullanıcı girişi
    """
    # Kullanıcıyı bul
    result = await db.execute(
        select(Kullanici).where(
            or_(
                Kullanici.email == request.email_veya_telefon,
                Kullanici.telefon.contains(request.email_veya_telefon[-10:])
            ),
            Kullanici.silinme_tarihi.is_(None)
        )
    )
    kullanici = result.scalar_one_or_none()
    
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"basarili": False, "hata": {"kod": "YANLIS_BILGI", "mesaj": "E-posta/telefon veya şifre hatalı."}}
        )
    
    # Şifre kontrolü
    if not verify_password(request.sifre, kullanici.sifre_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"basarili": False, "hata": {"kod": "YANLIS_BILGI", "mesaj": "E-posta/telefon veya şifre hatalı."}}
        )
    
    # Token'lar oluştur
    access_token = create_access_token(str(kullanici.id))
    refresh_token_value, refresh_gecerlilik = create_refresh_token()
    
    # Refresh token kaydet
    refresh_token = RefreshToken(
        kullanici_id=kullanici.id,
        token=refresh_token_value,
        cihaz_id=request.cihaz_bilgisi.get("cihaz_id") if request.cihaz_bilgisi else None,
        gecerlilik=refresh_gecerlilik
    )
    db.add(refresh_token)
    
    # Son check-in
    result = await db.execute(
        select(Checkin).where(Checkin.kullanici_id == kullanici.id).order_by(Checkin.tarih.desc()).limit(1)
    )
    son_checkin = result.scalar_one_or_none()
    
    return GirisResponse(
        basarili=True,
        access_token=access_token,
        refresh_token=refresh_token_value,
        token_suresi=3600,
        kullanici=GirisKullaniciBilgi(
            id=str(kullanici.id),
            ad=kullanici.ad,
            soyad=kullanici.soyad,
            email=kullanici.email,
            profil_foto=kullanici.profil_foto,
            abonelik_durumu=kullanici.abonelik_tipi.value.lower(),
            son_checkin=son_checkin.tarih if son_checkin else None
        )
    )


@router.post("/logout", response_model=BasariliMesajResponse)
async def logout(
    kullanici: Kullanici = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Çıkış yap - mevcut refresh token'ları iptal et
    """
    await db.execute(
        RefreshToken.__table__.update()
        .where(RefreshToken.kullanici_id == kullanici.id)
        .values(iptal_edildi=True)
    )
    
    return BasariliMesajResponse(basarili=True, mesaj="Başarıyla çıkış yapıldı.")


@router.post("/refresh", response_model=TokenYenileResponse)
async def refresh_token(request: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    """
    Access token yenile
    """
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token == request.refresh_token,
            RefreshToken.iptal_edildi == False,
            RefreshToken.gecerlilik > datetime.utcnow()
        )
    )
    token_kaydi = result.scalar_one_or_none()
    
    if not token_kaydi:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"basarili": False, "hata": {"kod": "GECERSIZ_TOKEN", "mesaj": "Geçersiz veya süresi dolmuş refresh token."}}
        )
    
    # Yeni access token
    access_token = create_access_token(str(token_kaydi.kullanici_id))
    
    # Son kullanımı güncelle
    token_kaydi.son_kullanim = datetime.utcnow()
    
    return TokenYenileResponse(access_token=access_token, token_suresi=3600)


@router.post("/sifre-sifirla/istek", response_model=BasariliMesajResponse)
async def forgot_password(request: SifreSifirlamaIstekRequest, db: AsyncSession = Depends(get_db)):
    """
    Şifre sıfırlama isteği - e-posta gönder
    """
    result = await db.execute(select(Kullanici).where(Kullanici.email == request.email))
    kullanici = result.scalar_one_or_none()
    
    if kullanici:
        # Sıfırlama token'ı oluştur
        reset_token = str(uuid.uuid4())
        kod = DogrulamaKodu(
            kullanici_id=kullanici.id,
            kod=reset_token,
            tip=DogrulamaTipi.SIFRE_SIFIRLAMA,
            gecerlilik=datetime.utcnow() + timedelta(hours=1)
        )
        db.add(kod)
        
        # E-posta gönder
        await send_password_reset_email(request.email, kullanici.ad, reset_token)
    
    # Güvenlik: Her zaman aynı yanıt
    return BasariliMesajResponse(
        basarili=True,
        mesaj="Şifre sıfırlama bağlantısı e-posta adresinize gönderildi."
    )


@router.post("/sifre-sifirla/dogrula", response_model=BasariliMesajResponse)
async def reset_password(request: SifreSifirlamaDogrulaRequest, db: AsyncSession = Depends(get_db)):
    """
    Şifre sıfırlama - yeni şifre belirle
    """
    result = await db.execute(
        select(DogrulamaKodu).where(
            DogrulamaKodu.kod == request.token,
            DogrulamaKodu.tip == DogrulamaTipi.SIFRE_SIFIRLAMA,
            DogrulamaKodu.kullanildi == False,
            DogrulamaKodu.gecerlilik > datetime.utcnow()
        )
    )
    kod_kaydi = result.scalar_one_or_none()
    
    if not kod_kaydi:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"basarili": False, "hata": {"kod": "GECERSIZ_TOKEN", "mesaj": "Geçersiz veya süresi dolmuş token."}}
        )
    
    # Şifreyi güncelle
    result = await db.execute(select(Kullanici).where(Kullanici.id == kod_kaydi.kullanici_id))
    kullanici = result.scalar_one()
    kullanici.sifre_hash = hash_password(request.yeni_sifre)
    
    # Kodu kullanıldı işaretle
    kod_kaydi.kullanildi = True
    
    # Tüm refresh token'ları iptal et
    await db.execute(
        RefreshToken.__table__.update()
        .where(RefreshToken.kullanici_id == kullanici.id)
        .values(iptal_edildi=True)
    )
    
    return BasariliMesajResponse(
        basarili=True,
        mesaj="Şifreniz başarıyla değiştirildi. Lütfen tekrar giriş yapın."
    )


@router.post("/email-dogrula", response_model=BasariliMesajResponse)
async def verify_email(request: EmailDogrulamaRequest, db: AsyncSession = Depends(get_db)):
    """
    E-posta doğrulama
    """
    result = await db.execute(
        select(DogrulamaKodu).where(
            DogrulamaKodu.kod == request.dogrulama_kodu,
            DogrulamaKodu.tip == DogrulamaTipi.EMAIL,
            DogrulamaKodu.kullanildi == False,
            DogrulamaKodu.gecerlilik > datetime.utcnow()
        )
    )
    kod_kaydi = result.scalar_one_or_none()
    
    if not kod_kaydi:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"basarili": False, "hata": {"kod": "GECERSIZ_KOD", "mesaj": "Geçersiz veya süresi dolmuş doğrulama kodu."}}
        )
    
    # Kullanıcıyı doğrulanmış işaretle
    result = await db.execute(select(Kullanici).where(Kullanici.id == kod_kaydi.kullanici_id))
    kullanici = result.scalar_one()
    kullanici.email_dogrulandi = True
    
    # Kodu kullanıldı işaretle
    kod_kaydi.kullanildi = True
    
    return BasariliMesajResponse(basarili=True, mesaj="E-posta adresiniz doğrulandı.")


@router.post("/telefon-dogrula/gonder", response_model=BasariliMesajResponse)
async def send_phone_otp(request: TelefonOTPGonderRequest, db: AsyncSession = Depends(get_db)):
    """
    Telefon doğrulama OTP gönder
    """
    result = await db.execute(
        select(Kullanici).where(Kullanici.telefon.contains(request.telefon[-10:]))
    )
    kullanici = result.scalar_one_or_none()
    
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"basarili": False, "hata": {"kod": "BULUNAMADI", "mesaj": "Bu telefon numarası ile kayıtlı kullanıcı bulunamadı."}}
        )
    
    # OTP oluştur
    otp_kodu = generate_otp()
    kod = DogrulamaKodu(
        kullanici_id=kullanici.id,
        kod=otp_kodu,
        tip=DogrulamaTipi.TELEFON,
        gecerlilik=datetime.utcnow() + timedelta(minutes=10)
    )
    db.add(kod)
    
    # TODO: SMS gönder
    print(f"[SMS] OTP: {otp_kodu} -> {request.telefon}")
    
    return BasariliMesajResponse(basarili=True, mesaj="Doğrulama kodu telefonunuza gönderildi.")


@router.post("/telefon-dogrula/onayla", response_model=BasariliMesajResponse)
async def verify_phone_otp(request: TelefonOTPOnaylaRequest, db: AsyncSession = Depends(get_db)):
    """
    Telefon OTP doğrulama
    """
    result = await db.execute(
        select(Kullanici).where(Kullanici.telefon.contains(request.telefon[-10:]))
    )
    kullanici = result.scalar_one_or_none()
    
    if not kullanici:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"basarili": False, "hata": {"kod": "BULUNAMADI", "mesaj": "Kullanıcı bulunamadı."}}
        )
    
    result = await db.execute(
        select(DogrulamaKodu).where(
            DogrulamaKodu.kullanici_id == kullanici.id,
            DogrulamaKodu.kod == request.otp_kodu,
            DogrulamaKodu.tip == DogrulamaTipi.TELEFON,
            DogrulamaKodu.kullanildi == False,
            DogrulamaKodu.gecerlilik > datetime.utcnow()
        )
    )
    kod_kaydi = result.scalar_one_or_none()
    
    if not kod_kaydi:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"basarili": False, "hata": {"kod": "GECERSIZ_KOD", "mesaj": "Geçersiz veya süresi dolmuş OTP kodu."}}
        )
    
    # Telefonu doğrulanmış işaretle
    kullanici.telefon_dogrulandi = True
    kod_kaydi.kullanildi = True
    
    return BasariliMesajResponse(basarili=True, mesaj="Telefon numaranız doğrulandı.")
