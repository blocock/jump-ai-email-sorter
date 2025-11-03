from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import json

from app.database import get_db
from app.models import User, GmailAccount
from app.schemas import TokenResponse, UserResponse
from app.auth import create_access_token, get_current_user
from app.config import settings

router = APIRouter(prefix="/auth", tags=["authentication"])

# Google OAuth configuration
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.modify',
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
    'openid'
]


def get_google_oauth_flow():
    """Create Google OAuth flow"""
    client_config = {
        "web": {
            "client_id": settings.GOOGLE_CLIENT_ID,
            "client_secret": settings.GOOGLE_CLIENT_SECRET,
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "redirect_uris": [f"{settings.BACKEND_URL}/auth/callback"]
        }
    }
    
    flow = Flow.from_client_config(
        client_config,
        scopes=SCOPES,
        redirect_uri=f"{settings.BACKEND_URL}/auth/callback"
    )
    return flow


@router.get("/login")
async def login():
    """Initiate Google OAuth login"""
    flow = get_google_oauth_flow()
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    return {"authorization_url": authorization_url, "state": state}


@router.get("/callback")
async def auth_callback(code: str, db: Session = Depends(get_db)):
    """Handle Google OAuth callback"""
    try:
        flow = get_google_oauth_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Get user info
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        
        google_id = user_info['id']
        email = user_info['email']
        name = user_info.get('name', email)
        
        # Check if user exists
        user = db.query(User).filter(User.google_id == google_id).first()
        
        if not user:
            # Create new user
            user = User(
                google_id=google_id,
                email=email,
                name=name
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Check if Gmail account exists
        gmail_account = db.query(GmailAccount).filter(
            GmailAccount.user_id == user.id,
            GmailAccount.email == email
        ).first()
        
        if not gmail_account:
            # Create Gmail account
            gmail_account = GmailAccount(
                user_id=user.id,
                email=email,
                access_token=credentials.token,
                refresh_token=credentials.refresh_token,
                token_expiry=credentials.expiry,
                is_primary=True
            )
            db.add(gmail_account)
        else:
            # Update tokens
            gmail_account.access_token = credentials.token
            gmail_account.refresh_token = credentials.refresh_token or gmail_account.refresh_token
            gmail_account.token_expiry = credentials.expiry
        
        db.commit()
        
        # Create JWT token
        access_token = create_access_token(data={"user_id": user.id})
        
        # Redirect to frontend with token
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/success?token={access_token}"
        )
        
    except Exception as e:
        print(f"Auth error: {e}")
        return RedirectResponse(
            url=f"{settings.FRONTEND_URL}/auth/error?message={str(e)}"
        )


@router.post("/connect-account")
async def connect_additional_account(code: str, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Connect an additional Gmail account"""
    try:
        flow = get_google_oauth_flow()
        flow.fetch_token(code=code)
        
        credentials = flow.credentials
        
        # Get user info
        user_info_service = build('oauth2', 'v2', credentials=credentials)
        user_info = user_info_service.userinfo().get().execute()
        
        email = user_info['email']
        
        # Check if this account is already connected
        existing = db.query(GmailAccount).filter(
            GmailAccount.user_id == current_user.id,
            GmailAccount.email == email
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This Gmail account is already connected"
            )
        
        # Create new Gmail account
        gmail_account = GmailAccount(
            user_id=current_user.id,
            email=email,
            access_token=credentials.token,
            refresh_token=credentials.refresh_token,
            token_expiry=credentials.expiry,
            is_primary=False
        )
        db.add(gmail_account)
        db.commit()
        db.refresh(gmail_account)
        
        return {"message": "Account connected successfully", "email": email}
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
