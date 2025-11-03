from pydantic import BaseModel, EmailStr
from datetime import datetime
from typing import Optional, List


class UserBase(BaseModel):
    email: EmailStr
    name: Optional[str] = None


class UserCreate(UserBase):
    google_id: str


class UserResponse(UserBase):
    id: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class GmailAccountBase(BaseModel):
    email: EmailStr


class GmailAccountCreate(GmailAccountBase):
    access_token: str
    refresh_token: str
    token_expiry: Optional[datetime] = None


class GmailAccountResponse(GmailAccountBase):
    id: int
    is_primary: bool
    created_at: datetime
    last_synced: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class CategoryBase(BaseModel):
    name: str
    description: str


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime
    email_count: Optional[int] = 0
    
    class Config:
        from_attributes = True


class EmailBase(BaseModel):
    subject: str
    sender: str
    sender_email: EmailStr
    received_at: datetime


class EmailCreate(EmailBase):
    gmail_message_id: str
    thread_id: str
    body_text: str
    body_html: Optional[str] = None
    recipient: str
    headers: Optional[dict] = None
    labels: Optional[List[str]] = None


class EmailResponse(EmailBase):
    id: int
    gmail_message_id: str
    ai_summary: str
    is_archived: bool
    is_deleted: bool
    unsubscribe_link: Optional[str] = None
    created_at: datetime
    category_id: int
    
    class Config:
        from_attributes = True


class EmailDetail(EmailResponse):
    body_text: str
    body_html: Optional[str] = None
    thread_id: str
    headers: Optional[dict] = None
    
    class Config:
        from_attributes = True


class BulkActionRequest(BaseModel):
    email_ids: List[int]
    action: str  # "delete" or "unsubscribe"


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

