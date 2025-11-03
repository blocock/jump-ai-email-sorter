import pytest
from unittest.mock import Mock, patch, MagicMock
from app.gmail_service import GmailService
from datetime import datetime

@pytest.fixture
def gmail_service():
    with patch('app.gmail_service.build') as mock_build:
        # Create a mock service
        mock_service = MagicMock()
        mock_build.return_value = mock_service
        
        service = GmailService(
            access_token="test_token",
            refresh_token="test_refresh",
            client_id="test_client_id",
            client_secret="test_client_secret"
        )
        
        # Attach the mock service so tests can use it
        service.service = mock_service
        
        return service

def test_parse_email_address(gmail_service):
    # Test with name and email
    name, email = gmail_service._parse_email_address('"John Doe" <john@example.com>')
    assert name == "John Doe"
    assert email == "john@example.com"
    
    # Test with just email
    name, email = gmail_service._parse_email_address('john@example.com')
    assert name == "john@example.com"
    assert email == "john@example.com"

def test_get_user_info(gmail_service):
    with patch.object(gmail_service.service.users(), 'getProfile') as mock_profile:
        mock_profile.return_value.execute.return_value = {
            'emailAddress': 'test@example.com',
            'messagesTotal': 100,
            'threadsTotal': 50
        }
        
        info = gmail_service.get_user_info()
        
        assert info['email'] == 'test@example.com'
        assert info['messages_total'] == 100
        assert info['threads_total'] == 50

def test_archive_message(gmail_service):
    with patch.object(gmail_service.service.users().messages(), 'modify') as mock_modify:
        mock_modify.return_value.execute.return_value = {}
        
        result = gmail_service.archive_message('test_message_id')
        
        assert result is True
        mock_modify.assert_called_once()

def test_delete_message(gmail_service):
    with patch.object(gmail_service.service.users().messages(), 'trash') as mock_trash:
        mock_trash.return_value.execute.return_value = {}
        
        result = gmail_service.delete_message('test_message_id')
        
        assert result is True
        mock_trash.assert_called_once()

