"""
SQLAlchemy Modelleri - Kullanıcı ve ilişkili tablolar
"""
import uuid
from datetime import datetime
from enum import Enum as PyEnum
from sqlalchemy import (
    Column, String, Boolean, DateTime, Float, Integer, 
    ForeignKey, Text, Enum, JSON
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base


# ==================== ENUM'LAR ====================

class Cinsiyet(str, PyEnum):
    ERKEK = "ERKEK"
    KADIN = "KADIN"
    BELIRTMEK_ISTEMIYORUM = "BELIRTMEK_ISTEMIYORUM"


class AbonelikTipi(str, PyEnum):
    UCRETSIZ = "UCRETSIZ"
    PREMIUM = "PREMIUM"


class RuhHali(str, PyEnum):
    IYI = "IYI"
    ORTA = "ORTA"
    KOTU = "KOTU"


class Iliski(str, PyEnum):
    AILE = "AILE"
    ARKADAS = "ARKADAS"
    KOMSU = "KOMSU"
    DIGER = "DIGER"


class Platform(str, PyEnum):
    IOS = "IOS"
    ANDROID = "ANDROID"


class AlarmTipi(str, PyEnum):
    OTOMATIK = "OTOMATIK"
    MANUEL = "MANUEL"
    PANIK = "PANIK"


class AlarmDurum(str, PyEnum):
    AKTIF = "AKTIF"
    IPTAL_EDILDI = "IPTAL_EDILDI"
    COZUMLENDI = "COZUMLENDI"


class BildirimTipi(str, PyEnum):
    HATIRLATMA = "HATIRLATMA"
    UYARI = "UYARI"
    ALARM = "ALARM"
    SISTEM = "SISTEM"


class DogrulamaTipi(str, PyEnum):
    EMAIL = "EMAIL"
    TELEFON = "TELEFON"
    SIFRE_SIFIRLAMA = "SIFRE_SIFIRLAMA"


# ==================== KULLANICI ====================

class Kullanici(Base):
    __tablename__ = "kullanicilar"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    telefon = Column(String(20), unique=True, nullable=False, index=True)
    sifre_hash = Column(String(255), nullable=False)
    ad = Column(String(50), nullable=False)
    soyad = Column(String(50), nullable=False)
    profil_foto = Column(String(500), nullable=True)
    dogum_tarihi = Column(DateTime, nullable=True)
    cinsiyet = Column(Enum(Cinsiyet), nullable=True)
    
    # Adres (JSON)
    adres = Column(JSON, nullable=True)
    
    # Doğrulama durumları
    email_dogrulandi = Column(Boolean, default=False)
    telefon_dogrulandi = Column(Boolean, default=False)
    
    # Abonelik
    abonelik_tipi = Column(Enum(AbonelikTipi), default=AbonelikTipi.UCRETSIZ)
    abonelik_bitis = Column(DateTime, nullable=True)
    
    # Check-in ayarları
    checkin_suresi_saat = Column(Integer, default=24)
    konum_paylasimi = Column(Boolean, default=True)
    
    # Zaman damgaları
    olusturma_tarihi = Column(DateTime, default=datetime.utcnow)
    guncelleme_tarihi = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    silinme_tarihi = Column(DateTime, nullable=True)
    
    # İlişkiler
    checkinler = relationship("Checkin", back_populates="kullanici", cascade="all, delete-orphan")
    acil_kisiler = relationship("AcilKisi", back_populates="kullanici", cascade="all, delete-orphan")
    cihazlar = relationship("Cihaz", back_populates="kullanici", cascade="all, delete-orphan")
    alarmlar = relationship("Alarm", back_populates="kullanici", cascade="all, delete-orphan")
    bildirimler = relationship("Bildirim", back_populates="kullanici", cascade="all, delete-orphan")
    refresh_tokenlar = relationship("RefreshToken", back_populates="kullanici", cascade="all, delete-orphan")
    dogrulama_kodlari = relationship("DogrulamaKodu", back_populates="kullanici", cascade="all, delete-orphan")


# ==================== CHECK-IN ====================

class Checkin(Base):
    __tablename__ = "checkinler"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kullanici_id = Column(UUID(as_uuid=True), ForeignKey("kullanicilar.id", ondelete="CASCADE"), nullable=False)
    tarih = Column(DateTime, default=datetime.utcnow)
    
    # Konum
    enlem = Column(Float, nullable=True)
    boylam = Column(Float, nullable=True)
    adres = Column(String(500), nullable=True)
    
    # Ek bilgiler
    not_ = Column("not", Text, nullable=True)
    ruh_hali = Column(Enum(RuhHali), nullable=True)
    
    # İlişkiler
    kullanici = relationship("Kullanici", back_populates="checkinler")


# ==================== ACİL DURUM KİŞİLERİ ====================

class AcilKisi(Base):
    __tablename__ = "acil_kisiler"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kullanici_id = Column(UUID(as_uuid=True), ForeignKey("kullanicilar.id", ondelete="CASCADE"), nullable=False)
    
    ad = Column(String(50), nullable=False)
    soyad = Column(String(50), nullable=False)
    telefon = Column(String(20), nullable=False)
    email = Column(String(255), nullable=True)
    iliski = Column(Enum(Iliski), default=Iliski.DIGER)
    oncelik = Column(Integer, default=1)
    ozel_mesaj = Column(Text, nullable=True)
    
    # Doğrulama
    dogrulandi = Column(Boolean, default=False)
    dogrulama_kodu = Column(String(10), nullable=True)
    
    # Zaman damgaları
    ekleme_tarihi = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kullanici = relationship("Kullanici", back_populates="acil_kisiler")


# ==================== CİHAZLAR ====================

class Cihaz(Base):
    __tablename__ = "cihazlar"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kullanici_id = Column(UUID(as_uuid=True), ForeignKey("kullanicilar.id", ondelete="CASCADE"), nullable=False)
    
    cihaz_id = Column(String(255), nullable=False)
    cihaz_adi = Column(String(100), nullable=True)
    platform = Column(Enum(Platform), nullable=False)
    push_token = Column(String(500), nullable=True)
    
    son_aktif = Column(DateTime, default=datetime.utcnow)
    olusturma_tarihi = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kullanici = relationship("Kullanici", back_populates="cihazlar")


# ==================== ALARMLAR ====================

class Alarm(Base):
    __tablename__ = "alarmlar"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kullanici_id = Column(UUID(as_uuid=True), ForeignKey("kullanicilar.id", ondelete="CASCADE"), nullable=False)
    
    tip = Column(Enum(AlarmTipi), nullable=False)
    durum = Column(Enum(AlarmDurum), default=AlarmDurum.AKTIF)
    mesaj = Column(Text, nullable=True)
    
    # Konum
    enlem = Column(Float, nullable=True)
    boylam = Column(Float, nullable=True)
    
    # Bilgilendirme
    bilgilendirilenler = Column(JSON, nullable=True)
    
    # Zaman damgaları
    tarih = Column(DateTime, default=datetime.utcnow)
    iptal_tarihi = Column(DateTime, nullable=True)
    iptal_nedeni = Column(Text, nullable=True)
    
    # İlişkiler
    kullanici = relationship("Kullanici", back_populates="alarmlar")


# ==================== BİLDİRİMLER ====================

class Bildirim(Base):
    __tablename__ = "bildirimler"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kullanici_id = Column(UUID(as_uuid=True), ForeignKey("kullanicilar.id", ondelete="CASCADE"), nullable=False)
    
    baslik = Column(String(200), nullable=False)
    icerik = Column(Text, nullable=False)
    tip = Column(Enum(BildirimTipi), nullable=False)
    okundu = Column(Boolean, default=False)
    
    tarih = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kullanici = relationship("Kullanici", back_populates="bildirimler")


# ==================== REFRESH TOKEN ====================

class RefreshToken(Base):
    __tablename__ = "refresh_tokenlar"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kullanici_id = Column(UUID(as_uuid=True), ForeignKey("kullanicilar.id", ondelete="CASCADE"), nullable=False)
    
    token = Column(String(255), unique=True, nullable=False)
    cihaz_id = Column(String(255), nullable=True)
    
    olusturma_tarihi = Column(DateTime, default=datetime.utcnow)
    son_kullanim = Column(DateTime, default=datetime.utcnow)
    gecerlilik = Column(DateTime, nullable=False)
    iptal_edildi = Column(Boolean, default=False)
    
    # İlişkiler
    kullanici = relationship("Kullanici", back_populates="refresh_tokenlar")


# ==================== DOĞRULAMA KODLARI ====================

class DogrulamaKodu(Base):
    __tablename__ = "dogrulama_kodlari"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kullanici_id = Column(UUID(as_uuid=True), ForeignKey("kullanicilar.id", ondelete="CASCADE"), nullable=False)
    
    kod = Column(String(100), nullable=False)
    tip = Column(Enum(DogrulamaTipi), nullable=False)
    gecerlilik = Column(DateTime, nullable=False)
    kullanildi = Column(Boolean, default=False)
    
    olusturma_tarihi = Column(DateTime, default=datetime.utcnow)
    
    # İlişkiler
    kullanici = relationship("Kullanici", back_populates="dogrulama_kodlari")


# ==================== SSS ====================

class SSS(Base):
    __tablename__ = "sss"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    kategori = Column(String(100), nullable=False)
    soru = Column(Text, nullable=False)
    cevap = Column(Text, nullable=False)
    sira = Column(Integer, default=0)
    aktif = Column(Boolean, default=True)
    
    olusturma_tarihi = Column(DateTime, default=datetime.utcnow)
