"""
Öldün mü? API - FastAPI Ana Uygulama (Supabase Entegrasyonu)
"""
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager

from app.config import get_settings
from app.routers.auth import router as auth_router
from app.routers.contacts import router as contacts_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Uygulama başlangıç ve kapanış olayları"""
    print("🚀 Uygulama başlatılıyor... (Supabase)")
    yield
    print("👋 Uygulama kapatılıyor...")


# FastAPI uygulaması
app = FastAPI(
    title="Öldün mü? API",
    description="""
    ## Yalnız yaşayanlar için güvenlik uygulaması API'si
    
    Bu API, "Öldün mü?" mobil uygulaması için backend hizmetleri sağlar.
    
    ### Özellikler
    - 🔐 **Kimlik Doğrulama**: Kayıt, giriş, şifre sıfırlama
    - ✅ **Check-in**: Günlük güvenlik kontrolü
    - 👨‍👩‍👧‍👦 **Acil Durum Kişileri**: Güvenilir kişi yönetimi
    - 🚨 **Alarm Sistemi**: Otomatik ve manuel alarm
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# CORS ayarları
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global hata yakalama
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    print(f"❌ Hata: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "error": {
                "code": "SERVER_ERROR",
                "message": "Bir hata oluştu. Lütfen daha sonra tekrar deneyin."
            }
        }
    )


# Router'ları ekle
app.include_router(auth_router, prefix="/v1")
app.include_router(contacts_router, prefix="/v1")


# Sağlık kontrolü
@app.get("/health", tags=["Sistem"])
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}


@app.get("/", tags=["Sistem"])
async def root():
    return {
        "app": "Öldün mü? API",
        "version": "1.0.0",
        "docs": "/docs"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG
    )
