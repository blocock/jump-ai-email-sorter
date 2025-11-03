from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.models import User, GmailAccount
from app.schemas import GmailAccountResponse
from app.auth import get_current_user

router = APIRouter(prefix="/accounts", tags=["accounts"])


@router.get("/", response_model=List[GmailAccountResponse])
async def list_gmail_accounts(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all connected Gmail accounts"""
    accounts = db.query(GmailAccount).filter(
        GmailAccount.user_id == current_user.id
    ).all()
    
    return accounts


@router.delete("/{account_id}")
async def disconnect_gmail_account(
    account_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Disconnect a Gmail account"""
    account = db.query(GmailAccount).filter(
        GmailAccount.id == account_id,
        GmailAccount.user_id == current_user.id
    ).first()
    
    if not account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Account not found"
        )
    
    # Don't allow disconnecting the last account
    account_count = db.query(GmailAccount).filter(
        GmailAccount.user_id == current_user.id
    ).count()
    
    if account_count <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot disconnect your only Gmail account"
        )
    
    db.delete(account)
    db.commit()
    
    return {"message": "Account disconnected successfully"}

