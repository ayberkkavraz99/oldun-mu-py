# 🚨 Öldün mü? - Mobil Uygulama Backend API (Supabase Entegrasyonlu)

> Yalnız yaşayan kişiler için güvenlik uygulaması backend servisi.

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green.svg)](https://fastapi.tiangolo.com)
[![Supabase](https://img.shields.io/badge/Supabase-Powered-green.svg)](https://supabase.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📖 Proje Hakkında

**"Öldün mü?"** uygulaması, yalnız yaşayan kişilerin güvenliğini sağlamak için tasarlanmış bir mobil uygulamanın backend API'sidir. 

Uygulama, kullanıcıların belirli aralıklarla "check-in" yapmasını bekler. Belirlenen süre içinde yanıt verilmezse, önceden tanımlanan acil durum kişilerine (Contacts) otomatik olarak alarm bildirimi gönderilmesi planlanmaktadır.

---

## ✨ Mevcut Özellikler

### 🔐 Kimlik Doğrulama (`auth`)
- **Kayıt (Sign Up)**: E-posta, isim-soyad ve şifre ile yeni hesap oluşturma.
- **Giriş (Login)**: JWT tabanlı güvenli oturum yönetimi.
- **Kullanıcı Bilgisi**: Giriş yapmış kullanıcının profil detaylarına erişim.

### 👨‍👩‍👧‍👦 Acil Durum Kişileri (`contacts`)
- **Liste**: Kullanıcıya ait acil durum kişilerinin listelenmesi.
- **Ekleme**: Yeni kişi ekleme (Ad, Telefon, E-posta).
- **Güncelleme**: Mevcut kişi bilgilerini düzenleme.
- **Silme**: Kişi kaydı silme.

---

## 🛠️ Teknoloji Yığını

| Kategori | Teknoloji |
|----------|-----------|
| **Backend Framework** | FastAPI (Python 3.10+) |
| **Veritabanı** | Supabase (PostgreSQL) |
| **Kimlik Doğrulama** | JWT (python-jose) |
| **Şifreleme** | bcrypt (passlib) |
| **Validasyon** | Pydantic v2 |
| **API Sunucusu** | Uvicorn (ASGI) |

---

## 📁 Veritabanı Şeması (Supabase)

### Users Tablosu
```sql
CREATE TABLE public.users (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    email character varying NOT NULL UNIQUE,
    password_hash character varying NOT NULL,
    first_name character varying,
    last_name character varying,
    phone_number character varying,
    is_active boolean DEFAULT true,
    is_verified boolean DEFAULT false,
    role character varying DEFAULT 'user',
    last_login_at timestamp with time zone,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT users_pkey PRIMARY KEY (id)
);
```

### Contacts Tablosu
```sql
CREATE TABLE public.contacts (
    id uuid NOT NULL DEFAULT gen_random_uuid(),
    user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    name character varying(100) NOT NULL,
    phone_number character varying(20) NOT NULL,
    email character varying(255) NULL,
    created_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    updated_at timestamp with time zone DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT contacts_pkey PRIMARY KEY (id),
    CONSTRAINT unique_user_phone UNIQUE (user_id, phone_number)
);
```

---

## 🚀 Kurulum ve Çalıştırma

### 1. Gereksinimler
- Python 3.10+
- Bir Supabase projesi

### 2. Hazırlık
```bash
# Proje dizinine git
cd oldun-mu-api-python

# Virtual environment oluştur ve aktif et
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Bağımlılıkları yükle
pip install -r requirements.txt
```

### 3. Ortam Değişkenleri
`app/database.py` dosyası içerisindeki `SUPABASE_URL` ve `SUPABASE_KEY` bilgilerini kendi projenize göre güncelleyin.

### 4. Uygulamayı Başlat
```bash
uvicorn app.main:app --reload --port 3000
```

API dokümantasyonuna şu adresten erişebilirsiniz: `http://localhost:3000/docs`

---

## 🔌 API Endpoint'leri

### Kimlik Doğrulama (`/v1/auth`)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| POST | `/register` | Yeni kullanıcı kaydı |
| POST | `/login` | Giriş ve Token alma |
| GET | `/me` | Mevcut kullanıcı bilgileri |

### Acil Durum Kişileri (`/v1/contacts`)
| Method | Endpoint | Açıklama |
|--------|----------|----------|
| GET | `/` | Kişileri listele |
| POST | `/` | Yeni kişi ekle |
| PUT | `/{contact_id}` | Kişi güncelle |
| DELETE | `/{contact_id}` | Kişi sil |

---

## 🚧 Yapılacaklar (Roadmap)

- [ ] **Check-in Sistemi**: Kullanıcının günlük durum bildirme mekanizması.
- [ ] **Alarm Sistemi**: Check-in yapılmadığında tetiklenen alarm süreci.
- [ ] **Bildirim Servisi**: SMS ve Push bildirim entegrasyonları.
- [ ] **Abonelik**: Premium özellikler için ödeme entegrasyonu.

---

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

<p align="center">
  <b>🛡️ Güvenliğiniz için buradayız</b><br>
  <i>"Öldün mü?" - Yalnız yaşayanlar için güvenlik uygulaması</i>
</p>
