# 🚨 Öldün mü? - Mobil Uygulama Backend API

> Yalnız yaşayan kişiler için güvenlik uygulaması

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue.svg)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Proje Hakkında

**"Öldün mü?"** uygulaması, yalnız yaşayan kişilerin güvenliğini sağlamak için tasarlanmış bir mobil uygulamanın backend API'sidir. 

Uygulama, kullanıcıların belirli aralıklarla "check-in" yapmasını bekler. Belirlenen süre içinde yanıt verilmezse, önceden tanımlanan acil durum kişilerine otomatik olarak alarm bildirimi gönderilir.

### 🎯 Hedef Kitle
- Yalnız yaşayan bireyler
- Yaşlı bireyler ve onların yakınları
- Uzak bölgelerde çalışan kişiler
- Kronik hastalığı olan bireyler

---

## ✨ Özellikler

### 🔐 Kimlik Doğrulama
- E-posta ve telefon ile kayıt
- JWT tabanlı güvenli oturum yönetimi
- Şifre sıfırlama ve e-posta doğrulama
- SMS OTP ile telefon doğrulama
- Çoklu cihaz desteği

### ✅ Check-in Sistemi (Ana Özellik)
- Tek dokunuşla günlük check-in
- Konum paylaşımı (opsiyonel)
- Ruh hali takibi
- Özelleştirilebilir check-in aralığı (24-48 saat)
- Otomatik hatırlatma bildirimleri

### 👨‍👩‍👧‍👦 Acil Durum Kişileri
- 2-5 arası güvenilir kişi ekleme (abonelik tipine göre)
- Öncelik sıralaması
- SMS ile kişi doğrulama
- Özel mesaj tanımlama

### 🚨 Alarm Sistemi
- **Otomatik Alarm**: Check-in süresi aşıldığında
- **Manuel Alarm**: Panik butonu ile anında
- Çoklu bildirim kanalı (SMS, E-posta, Push)
- Alarm iptali ve geri bildirim

### 📊 İstatistikler
- Check-in geçmişi ve raporlar
- Ardışık gün takibi
- Ruh hali analizi

### 💳 Abonelik Sistemi
- **Ücretsiz Plan**: Temel özellikler
- **Premium Plan**: Tüm özellikler + öncelikli destek

---

## 🛠️ Teknoloji Yığını

| Kategori | Teknoloji |
|----------|-----------|
| **Backend Framework** | FastAPI (Python 3.10+) |
| **Veritabanı** | PostgreSQL 15+ |
| **ORM** | SQLAlchemy 2.0 (Async) |
| **Migrasyon** | Alembic |
| **Kimlik Doğrulama** | JWT (python-jose) |
| **Şifreleme** | bcrypt (passlib) |
| **Validasyon** | Pydantic v2 |
| **E-posta** | aiosmtplib |
| **API Sunucusu** | Uvicorn (ASGI) |

---

## 📁 Proje Yapısı

```
oldun-mu-api-python/
│
├── app/                          # Ana uygulama paketi
│   ├── __init__.py
│   ├── main.py                   # FastAPI uygulama girişi
│   ├── config.py                 # Ortam değişkenleri ve ayarlar
│   ├── database.py               # Veritabanı bağlantısı
│   │
│   ├── models/                   # SQLAlchemy modelleri
│   │   ├── __init__.py
│   │   └── models.py             # Tüm veritabanı tabloları
│   │
│   ├── schemas/                  # Pydantic şemaları (Request/Response)
│   │   ├── __init__.py
│   │   ├── auth.py               # Kimlik doğrulama şemaları
│   │   ├── kullanici.py          # Kullanıcı şemaları
│   │   ├── checkin.py            # Check-in şemaları
│   │   ├── acil_kisi.py          # Acil kişi şemaları
│   │   ├── alarm.py              # Alarm şemaları
│   │   └── genel.py              # Genel yanıt şemaları
│   │
│   ├── routers/                  # API endpoint'leri
│   │   ├── __init__.py
│   │   ├── auth.py               # /auth/* endpoint'leri
│   │   ├── kullanici.py          # /kullanici/* endpoint'leri
│   │   ├── checkin.py            # /checkin/* endpoint'leri
│   │   ├── acil_kisi.py          # /acil-kisiler/* endpoint'leri
│   │   └── alarm.py              # /alarm/*, /bildirimler/* endpoint'leri
│   │
│   ├── services/                 # İş mantığı servisleri
│   │   ├── __init__.py
│   │   └── email_service.py      # E-posta gönderimi
│   │
│   └── utils/                    # Yardımcı fonksiyonlar
│       ├── __init__.py
│       └── security.py           # JWT, şifre hashleme, auth
│
├── alembic/                      # Veritabanı migrasyonları
│   ├── versions/                 # Migrasyon dosyaları
│   ├── env.py
│   └── script.py.mako
│
├── uploads/                      # Yüklenen dosyalar (profil fotoları)
│
├── .env.example                  # Örnek ortam değişkenleri
├── .gitignore
├── alembic.ini                   # Alembic konfigürasyonu
├── requirements.txt              # Python bağımlılıkları
└── README.md                     # Bu dosya
```

---

## 🚀 Kurulum

### Gereksinimler
- Python 3.10 veya üzeri
- PostgreSQL 15 veya üzeri
- pip (Python paket yöneticisi)

### 1. Projeyi Klonla
```bash
git clone <repo-url>
cd oldun-mu-api-python
```

### 2. Virtual Environment Oluştur
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Bağımlılıkları Yükle
```bash
pip install -r requirements.txt
```

### 4. Ortam Değişkenlerini Ayarla
```bash
# .env.example dosyasını kopyala
cp .env.example .env

# .env dosyasını düzenle
# - DATABASE_URL: PostgreSQL bağlantı URL'i
# - JWT_SECRET_KEY: Güvenli bir secret key
# - SMTP_*: E-posta sunucu bilgileri
```

### 5. Veritabanını Oluştur
```bash
# PostgreSQL'de veritabanı oluştur
createdb oldunmu_db

# Tabloları oluştur (Alembic ile)
alembic upgrade head
```

### 6. Uygulamayı Başlat
```bash
# Development modu
uvicorn app.main:app --reload --port 3000

# Production modu
uvicorn app.main:app --host 0.0.0.0 --port 3000
```

---

## 📚 API Dokümantasyonu

Uygulama çalışırken aşağıdaki adreslerde otomatik dokümantasyona erişebilirsiniz:

| Adres | Açıklama |
|-------|----------|
| `http://localhost:3000/docs` | Swagger UI (interaktif) |
| `http://localhost:3000/redoc` | ReDoc (okunabilir) |
| `http://localhost:3000/openapi.json` | OpenAPI şeması |

---

## 🔌 API Endpoint'leri

### Kimlik Doğrulama (`/v1/auth`)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/register` | Yeni kullanıcı kaydı |
| POST | `/login` | Giriş yap |
| POST | `/logout` | Çıkış yap |
| POST | `/refresh` | Token yenile |
| POST | `/sifre-sifirla/istek` | Şifre sıfırlama isteği |
| POST | `/sifre-sifirla/dogrula` | Yeni şifre belirle |
| POST | `/email-dogrula` | E-posta doğrula |
| POST | `/telefon-dogrula/gonder` | SMS OTP gönder |
| POST | `/telefon-dogrula/onayla` | SMS OTP doğrula |

### Kullanıcı (`/v1/kullanici`)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/profil` | Profil bilgilerini getir |
| PUT | `/profil` | Profil güncelle |
| POST | `/profil-foto` | Profil fotoğrafı yükle |
| PUT | `/sifre-degistir` | Şifre değiştir |
| DELETE | `/hesap` | Hesabı sil |

### Check-in (`/v1/checkin`)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/` | Check-in yap |
| GET | `/gecmis` | Check-in geçmişi |
| GET | `/durum` | Check-in durumu |
| POST | `/ertele` | Hatırlatma ertele |

### Acil Durum Kişileri (`/v1/acil-kisiler`)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/` | Kişileri listele |
| POST | `/` | Kişi ekle |
| PUT | `/{kisi_id}` | Kişi güncelle |
| DELETE | `/{kisi_id}` | Kişi sil |

### Alarm (`/v1/alarm`)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/panik` | Panik butonu |
| POST | `/iptal` | Alarmı iptal et |
| GET | `/gecmis` | Alarm geçmişi |

### Bildirimler (`/v1/bildirimler`)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/ayarlar` | Bildirim ayarları |
| PUT | `/ayarlar` | Ayarları güncelle |
| GET | `/gecmis` | Bildirim geçmişi |

---

## 🔐 Güvenlik

### Kimlik Doğrulama
- JWT Bearer Token kullanılır
- Access token süresi: 1 saat
- Refresh token süresi: 7 gün

### Şifreleme
- Şifreler bcrypt ile hashlenir (12 round)
- JWT secret key için güçlü anahtar kullanın

### API Güvenliği
- CORS koruması
- Rate limiting (100 istek/dakika)
- Input validation (Pydantic)

---

## 🧪 Test

```bash
# Test çalıştır
pytest

# Coverage raporu
pytest --cov=app --cov-report=html
```

---

## 📱 Mobil Uygulama Entegrasyonu

Bu API, Flutter, React Native veya native iOS/Android uygulamaları ile kullanılabilir.

### Örnek İstek (cURL)
```bash
# Kayıt
curl -X POST "http://localhost:3000/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "ad": "Ahmet",
    "soyad": "Yılmaz",
    "email": "ahmet@example.com",
    "telefon": "05551234567",
    "sifre": "Guclu123",
    "sifre_tekrar": "Guclu123"
  }'

# Check-in
curl -X POST "http://localhost:3000/v1/checkin" \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "konum": {"enlem": 41.0082, "boylam": 28.9784},
    "ruh_hali": "iyi"
  }'
```

---

## 🚧 Yapılacaklar (TODO)

- [ ] SMS servisi entegrasyonu (Twilio/Netgsm)
- [ ] Push notification (Firebase Cloud Messaging)
- [ ] Background job scheduler (check-in kontrolü)
- [ ] Ödeme sistemi entegrasyonu (iyzico/Stripe)
- [ ] Admin paneli
- [ ] Rate limiting middleware
- [ ] Logging sistemi
- [ ] Docker desteği
- [ ] Unit ve integration testleri

---

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

## 👥 İletişim

Sorularınız için: [email@example.com](mailto:email@example.com)

---

<p align="center">
  <b>🛡️ Güvenliğiniz için buradayız</b><br>
  <i>"Öldün mü?" - Yalnız yaşayanlar için güvenlik uygulaması</i>
</p>
