"""
Contacts Router - Acil Durum Kişileri Yönetimi
"""
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from datetime import datetime

from app.database import get_supabase
from app.schemas.contacts import ContactCreate, ContactUpdate, ContactResponse, ContactsListResponse
from app.utils.security import get_user_id_from_token

router = APIRouter(prefix="/contacts", tags=["Acil Durum Kişileri"])


@router.get("/", response_model=ContactsListResponse)
async def get_contacts(user_id: str = Depends(get_user_id_from_token)):
    """
    Giriş yapmış kullanıcının tüm acil durum kişilerini getirir
    """
    supabase = get_supabase()
    
    result = supabase.table("contacts").select("*").eq("user_id", user_id).order_by("created_at").execute()
    
    return ContactsListResponse(success=True, contacts=result.data)


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    request: ContactCreate, 
    user_id: str = Depends(get_user_id_from_token)
):
    """
    Yeni bir acil durum kişisi ekler
    """
    supabase = get_supabase()
    
    # Telefon numarası kontrolü (User bazlı unique constraint veritabanında var ama biz de kontrol edelim)
    existing = supabase.table("contacts").select("id").eq("user_id", user_id).eq("phone_number", request.phone_number).execute()
    
    if existing.data and len(existing.data) > 0:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"success": False, "error": {"code": "CONTACT_EXISTS", "message": "Bu telefon numarası zaten listenizde ekli."}}
        )
    
    contact_data = request.model_dump()
    contact_data["user_id"] = user_id
    
    result = supabase.table("contacts").insert(contact_data).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={"success": False, "error": {"code": "INSERT_FAILED", "message": "Kişi eklenirken bir hata oluştu."}}
        )
    
    return result.data[0]


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: str,
    request: ContactUpdate,
    user_id: str = Depends(get_user_id_from_token)
):
    """
    Belirli bir acil durum kişisini günceller
    """
    supabase = get_supabase()
    
    # Kişinin kullanıcıya ait olup olmadığını kontrol et
    check = supabase.table("contacts").select("id").eq("id", contact_id).eq("user_id", user_id).execute()
    
    if not check.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error": {"code": "NOT_FOUND", "message": "Kişi bulunamadı veya yetkiniz yok."}}
        )
    
    update_data = request.model_dump(exclude_unset=True)
    update_data["updated_at"] = datetime.utcnow().isoformat()
    
    result = supabase.table("contacts").update(update_data).eq("id", contact_id).execute()
    
    return result.data[0]


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_contact(
    contact_id: str,
    user_id: str = Depends(get_user_id_from_token)
):
    """
    Belirli bir acil durum kişisini siler
    """
    supabase = get_supabase()
    
    # Kişinin kullanıcıya ait olup olmadığını kontrol et
    check = supabase.table("contacts").select("id").eq("id", contact_id).eq("user_id", user_id).execute()
    
    if not check.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"success": False, "error": {"code": "NOT_FOUND", "message": "Kişi bulunamadı veya yetkiniz yok."}}
        )
    
    supabase.table("contacts").delete().eq("id", contact_id).execute()
    
    return None
