from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String)
    google_id = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    gmail_accounts = relationship("GmailAccount", back_populates="user", cascade="all, delete-orphan")
    categories = relationship("Category", back_populates="user", cascade="all, delete-orphan")


class GmailAccount(Base):
    __tablename__ = "gmail_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    email = Column(String, index=True)
    access_token = Column(Text)
    refresh_token = Column(Text)
    token_expiry = Column(DateTime, nullable=True)
    is_primary = Column(Boolean, default=False)
    history_id = Column(String, nullable=True)  # For Gmail push notifications
    created_at = Column(DateTime, default=datetime.utcnow)
    last_synced = Column(DateTime, nullable=True)
    
    user = relationship("User", back_populates="gmail_accounts")
    emails = relationship("Email", back_populates="gmail_account", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String, index=True)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    user = relationship("User", back_populates="categories")
    emails = relationship("Email", back_populates="category", cascade="all, delete-orphan")


class Email(Base):
    __tablename__ = "emails"
    
    id = Column(Integer, primary_key=True, index=True)
    gmail_account_id = Column(Integer, ForeignKey("gmail_accounts.id"))
    category_id = Column(Integer, ForeignKey("categories.id"))
    gmail_message_id = Column(String, unique=True, index=True)
    thread_id = Column(String, index=True)
    subject = Column(String)
    sender = Column(String)
    sender_email = Column(String)
    recipient = Column(String)
    received_at = Column(DateTime)
    body_text = Column(Text)
    body_html = Column(Text, nullable=True)
    ai_summary = Column(Text)
    headers = Column(JSON, nullable=True)
    labels = Column(JSON, nullable=True)
    is_archived = Column(Boolean, default=False)
    is_deleted = Column(Boolean, default=False)
    unsubscribe_link = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    gmail_account = relationship("GmailAccount", back_populates="emails")
    category = relationship("Category", back_populates="emails")

