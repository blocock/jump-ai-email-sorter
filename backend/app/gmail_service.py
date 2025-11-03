from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from datetime import datetime
from typing import List, Optional, Dict
import base64
import email
from email.utils import parsedate_to_datetime
from bs4 import BeautifulSoup
import re


class GmailService:
    SCOPES = [
        'https://www.googleapis.com/auth/gmail.readonly',
        'https://www.googleapis.com/auth/gmail.modify',
        'https://www.googleapis.com/auth/userinfo.email',
        'https://www.googleapis.com/auth/userinfo.profile'
    ]
    
    def __init__(self, access_token: str, refresh_token: str, client_id: str, client_secret: str):
        self.credentials = Credentials(
            token=access_token,
            refresh_token=refresh_token,
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=self.SCOPES
        )
        self.service = build('gmail', 'v1', credentials=self.credentials)
    
    def get_user_info(self):
        """Get user profile information"""
        try:
            profile = self.service.users().getProfile(userId='me').execute()
            return {
                'email': profile['emailAddress'],
                'messages_total': profile.get('messagesTotal', 0),
                'threads_total': profile.get('threadsTotal', 0)
            }
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def list_messages(self, query: str = '', max_results: int = 100, page_token: Optional[str] = None) -> Dict:
        """List messages matching the query"""
        try:
            params = {
                'userId': 'me',
                'maxResults': max_results,
                'q': query
            }
            if page_token:
                params['pageToken'] = page_token
            
            results = self.service.users().messages().list(**params).execute()
            return results
        except HttpError as error:
            print(f'An error occurred: {error}')
            return {'messages': [], 'resultSizeEstimate': 0}
    
    def get_message(self, message_id: str) -> Optional[Dict]:
        """Get a specific message by ID"""
        try:
            message = self.service.users().messages().get(
                userId='me',
                id=message_id,
                format='full'
            ).execute()
            return self._parse_message(message)
        except HttpError as error:
            print(f'An error occurred: {error}')
            return None
    
    def _parse_message(self, message: Dict) -> Dict:
        """Parse Gmail message into structured format"""
        headers = {header['name']: header['value'] for header in message['payload'].get('headers', [])}
        
        # Extract body
        body_text = ''
        body_html = ''
        
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                    body_text += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
                elif part['mimeType'] == 'text/html' and 'data' in part['body']:
                    body_html += base64.urlsafe_b64decode(part['body']['data']).decode('utf-8', errors='ignore')
        elif 'body' in message['payload'] and 'data' in message['payload']['body']:
            body_data = base64.urlsafe_b64decode(message['payload']['body']['data']).decode('utf-8', errors='ignore')
            if message['payload']['mimeType'] == 'text/plain':
                body_text = body_data
            elif message['payload']['mimeType'] == 'text/html':
                body_html = body_data
        
        # If only HTML, extract text
        if not body_text and body_html:
            soup = BeautifulSoup(body_html, 'html.parser')
            body_text = soup.get_text(separator='\n', strip=True)
        
        # Extract unsubscribe link
        unsubscribe_link = None
        if 'List-Unsubscribe' in headers:
            match = re.search(r'<(https?://[^>]+)>', headers['List-Unsubscribe'])
            if match:
                unsubscribe_link = match.group(1)
        
        # Also search in body
        if not unsubscribe_link:
            unsubscribe_patterns = [
                r'https?://[^\s]+unsubscribe[^\s]*',
                r'https?://[^\s]+opt-out[^\s]*',
                r'https?://[^\s]+remove[^\s]*'
            ]
            for pattern in unsubscribe_patterns:
                match = re.search(pattern, body_text, re.IGNORECASE)
                if match:
                    unsubscribe_link = match.group(0).rstrip('.,;)')
                    break
        
        # Parse date
        date_str = headers.get('Date', '')
        try:
            received_at = parsedate_to_datetime(date_str) if date_str else datetime.utcnow()
        except:
            received_at = datetime.utcnow()
        
        # Extract sender info
        from_header = headers.get('From', '')
        sender_name, sender_email = self._parse_email_address(from_header)
        
        return {
            'message_id': message['id'],
            'thread_id': message['threadId'],
            'subject': headers.get('Subject', '(No Subject)'),
            'sender': sender_name,
            'sender_email': sender_email,
            'recipient': headers.get('To', ''),
            'received_at': received_at,
            'body_text': body_text[:50000],  # Limit size
            'body_html': body_html[:100000] if body_html else None,
            'headers': dict(headers),
            'labels': message.get('labelIds', []),
            'unsubscribe_link': unsubscribe_link
        }
    
    def _parse_email_address(self, email_str: str) -> tuple:
        """Parse email address string into name and email"""
        match = re.match(r'^(.+?)\s*<(.+?)>$', email_str)
        if match:
            return match.group(1).strip('"'), match.group(2)
        return email_str, email_str
    
    def archive_message(self, message_id: str) -> bool:
        """Archive a message (remove INBOX label)"""
        try:
            self.service.users().messages().modify(
                userId='me',
                id=message_id,
                body={'removeLabelIds': ['INBOX']}
            ).execute()
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False
    
    def delete_message(self, message_id: str) -> bool:
        """Move message to trash"""
        try:
            self.service.users().messages().trash(
                userId='me',
                id=message_id
            ).execute()
            return True
        except HttpError as error:
            print(f'An error occurred: {error}')
            return False
    
    def get_new_messages_since(self, history_id: Optional[str] = None) -> List[Dict]:
        """Get new messages since a specific history ID"""
        if not history_id:
            # Get recent messages (last 24 hours)
            query = 'newer_than:1d'
            results = self.list_messages(query=query, max_results=100)
            messages = results.get('messages', [])
            return [self.get_message(msg['id']) for msg in messages]
        
        try:
            history = self.service.users().history().list(
                userId='me',
                startHistoryId=history_id,
                historyTypes=['messageAdded']
            ).execute()
            
            messages = []
            for record in history.get('history', []):
                for message_added in record.get('messagesAdded', []):
                    msg = self.get_message(message_added['message']['id'])
                    if msg:
                        messages.append(msg)
            
            return messages
        except HttpError as error:
            print(f'An error occurred: {error}')
            return []

