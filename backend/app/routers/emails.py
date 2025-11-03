from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import asyncio

from app.database import get_db
from app.models import User, Category, Email, GmailAccount
from app.schemas import EmailResponse, EmailDetail, BulkActionRequest
from app.auth import get_current_user
from app.gmail_service import GmailService
from app.ai_service import AIService
from app.unsubscribe_agent import unsubscribe_from_email
from app.config import settings

router = APIRouter(prefix="/emails", tags=["emails"])


@router.get("/category/{category_id}", response_model=List[EmailResponse])
async def list_emails_by_category(
    category_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List all emails in a specific category"""
    # Verify category belongs to user
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    emails = db.query(Email).filter(
        Email.category_id == category_id,
        Email.is_deleted == False
    ).order_by(Email.received_at.desc()).all()
    
    return emails


@router.get("/{email_id}", response_model=EmailDetail)
async def get_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get full email details"""
    email = db.query(Email).join(GmailAccount).filter(
        Email.id == email_id,
        GmailAccount.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    return email


@router.post("/sync")
async def sync_emails(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Sync new emails from all Gmail accounts"""
    gmail_accounts = db.query(GmailAccount).filter(
        GmailAccount.user_id == current_user.id
    ).all()
    
    if not gmail_accounts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No Gmail accounts connected"
        )
    
    # Start background sync
    background_tasks.add_task(sync_emails_task, current_user.id, db)
    
    return {"message": "Email sync started"}


def sync_emails_task(user_id: int, db: Session):
    """Background task to sync emails"""
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            return
        
        gmail_accounts = db.query(GmailAccount).filter(
            GmailAccount.user_id == user_id
        ).all()
        
        categories = db.query(Category).filter(
            Category.user_id == user_id
        ).all()
        
        if not categories:
            print("No categories defined, skipping sync")
            return
        
        categories_data = [
            {"id": cat.id, "name": cat.name, "description": cat.description}
            for cat in categories
        ]
        
        ai_service = AIService()
        
        for gmail_account in gmail_accounts:
            try:
                gmail_service = GmailService(
                    access_token=gmail_account.access_token,
                    refresh_token=gmail_account.refresh_token,
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET
                )
                
                # Get new messages
                messages = gmail_service.get_new_messages_since(gmail_account.history_id)
                
                for message in messages:
                    if not message:
                        continue
                    
                    # Check if already imported
                    existing = db.query(Email).filter(
                        Email.gmail_message_id == message['message_id']
                    ).first()
                    
                    if existing:
                        continue
                    
                    # Process email with AI
                    ai_result = ai_service.process_email(message, categories_data)
                    
                    if not ai_result['category_id']:
                        # Skip emails that don't match any category
                        continue
                    
                    # Create email record
                    email = Email(
                        gmail_account_id=gmail_account.id,
                        category_id=ai_result['category_id'],
                        gmail_message_id=message['message_id'],
                        thread_id=message['thread_id'],
                        subject=message['subject'],
                        sender=message['sender'],
                        sender_email=message['sender_email'],
                        recipient=message['recipient'],
                        received_at=message['received_at'],
                        body_text=message['body_text'],
                        body_html=message['body_html'],
                        ai_summary=ai_result['summary'],
                        headers=message['headers'],
                        labels=message['labels'],
                        unsubscribe_link=message.get('unsubscribe_link'),
                        is_archived=False
                    )
                    db.add(email)
                    db.commit()
                    
                    # Archive the email in Gmail
                    gmail_service.archive_message(message['message_id'])
                    email.is_archived = True
                    db.commit()
                
            except Exception as e:
                print(f"Error syncing emails for account {gmail_account.email}: {e}")
                continue
        
    except Exception as e:
        print(f"Error in sync task: {e}")


@router.post("/bulk-action")
async def bulk_action(
    action_request: BulkActionRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Perform bulk action on selected emails"""
    # Verify all emails belong to user
    emails = db.query(Email).join(GmailAccount).filter(
        Email.id.in_(action_request.email_ids),
        GmailAccount.user_id == current_user.id
    ).all()
    
    if len(emails) != len(action_request.email_ids):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some emails not found or don't belong to you"
        )
    
    if action_request.action == "delete":
        # Mark as deleted and delete from Gmail
        for email in emails:
            email.is_deleted = True
            
            gmail_account = email.gmail_account
            try:
                gmail_service = GmailService(
                    access_token=gmail_account.access_token,
                    refresh_token=gmail_account.refresh_token,
                    client_id=settings.GOOGLE_CLIENT_ID,
                    client_secret=settings.GOOGLE_CLIENT_SECRET
                )
                gmail_service.delete_message(email.gmail_message_id)
            except Exception as e:
                print(f"Error deleting email from Gmail: {e}")
        
        db.commit()
        return {"message": f"Deleted {len(emails)} emails"}
    
    elif action_request.action == "unsubscribe":
        # Start unsubscribe process in background
        background_tasks.add_task(unsubscribe_emails_task, [e.id for e in emails], db)
        return {"message": f"Started unsubscribe process for {len(emails)} emails"}
    
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid action. Must be 'delete' or 'unsubscribe'"
        )


async def unsubscribe_emails_task(email_ids: List[int], db: Session):
    """Background task to unsubscribe from emails"""
    for email_id in email_ids:
        email = db.query(Email).filter(Email.id == email_id).first()
        if not email or not email.unsubscribe_link:
            continue
        
        try:
            result = await unsubscribe_from_email(email.unsubscribe_link)
            print(f"Unsubscribe result for {email.sender_email}: {result}")
            
            # If successful, mark email as deleted
            if result.get('success'):
                email.is_deleted = True
                db.commit()
        except Exception as e:
            print(f"Error unsubscribing from {email.sender_email}: {e}")


@router.delete("/{email_id}")
async def delete_email(
    email_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a single email"""
    email = db.query(Email).join(GmailAccount).filter(
        Email.id == email_id,
        GmailAccount.user_id == current_user.id
    ).first()
    
    if not email:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Email not found"
        )
    
    # Mark as deleted
    email.is_deleted = True
    
    # Delete from Gmail
    gmail_account = email.gmail_account
    try:
        gmail_service = GmailService(
            access_token=gmail_account.access_token,
            refresh_token=gmail_account.refresh_token,
            client_id=settings.GOOGLE_CLIENT_ID,
            client_secret=settings.GOOGLE_CLIENT_SECRET
        )
        gmail_service.delete_message(email.gmail_message_id)
    except Exception as e:
        print(f"Error deleting email from Gmail: {e}")
    
    db.commit()
    
    return {"message": "Email deleted"}

