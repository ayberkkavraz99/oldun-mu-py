"""Routers package"""
from app.routers.auth import router as auth_router
from app.routers.kullanici import router as kullanici_router
from app.routers.checkin import router as checkin_router
from app.routers.acil_kisi import router as acil_kisi_router
from app.routers.alarm import router as alarm_router

__all__ = [
    "auth_router",
    "kullanici_router", 
    "checkin_router",
    "acil_kisi_router",
    "alarm_router",
]
