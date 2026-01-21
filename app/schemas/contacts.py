"""
Pydantic Şemaları - Contacts (Acil Durum Kişileri)
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List
from datetime import datetime


class ContactCreate(BaseModel):
    """Yeni kişi ekleme isteği"""
    name: str = Field(..., min_length=2, max_length=100, description="Kişinin adı")
    phone_number: str = Field(..., min_length=7, max_length=20, description="Telefon numarası")
    email: Optional[EmailStr] = Field(None, description="E-posta adresi")


class ContactUpdate(BaseModel):
    """Kişi güncelleme isteği"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    phone_number: Optional[str] = Field(None, min_length=7, max_length=20)
    email: Optional[EmailStr] = None


class ContactResponse(BaseModel):
    """Kişi bilgisi yanıtı"""
    id: str  # UUID as string
    user_id: str
    name: str
    phone_number: str
    email: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ContactsListResponse(BaseModel):
    """Kişi listesi yanıtı"""
    success: bool = True
    contacts: List[ContactResponse]
