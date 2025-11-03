import pytest
from unittest.mock import Mock, patch
from app.ai_service import AIService

@pytest.fixture
def ai_service():
    return AIService()

@pytest.fixture
def sample_email():
    return {
        "subject": "Weekly Newsletter",
        "sender": "News Corp",
        "sender_email": "news@example.com",
        "body_text": "This is our weekly newsletter with the latest updates..."
    }

@pytest.fixture
def sample_categories():
    return [
        {"id": 1, "name": "Newsletters", "description": "Marketing and promotional emails, newsletters"},
        {"id": 2, "name": "Receipts", "description": "Purchase receipts and order confirmations"},
        {"id": 3, "name": "Social", "description": "Social media notifications and updates"}
    ]

def test_summarize_email(ai_service, sample_email):
    with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "Weekly newsletter with latest updates"
        mock_create.return_value = mock_response
        
        summary = ai_service.summarize_email(sample_email)
        
        assert summary == "Weekly newsletter with latest updates"
        assert mock_create.called

def test_categorize_email(ai_service, sample_email, sample_categories):
    with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "1"
        mock_create.return_value = mock_response
        
        category_id = ai_service.categorize_email(sample_email, sample_categories)
        
        assert category_id == 1
        assert mock_create.called

def test_categorize_email_no_match(ai_service, sample_email, sample_categories):
    with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
        # Mock the OpenAI response indicating no match
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = "0"
        mock_create.return_value = mock_response
        
        category_id = ai_service.categorize_email(sample_email, sample_categories)
        
        assert category_id is None

def test_process_email(ai_service, sample_email, sample_categories):
    with patch.object(ai_service.client.chat.completions, 'create') as mock_create:
        # Mock responses for both categorization and summarization
        mock_response_cat = Mock()
        mock_response_cat.choices = [Mock()]
        mock_response_cat.choices[0].message.content = "1"
        
        mock_response_sum = Mock()
        mock_response_sum.choices = [Mock()]
        mock_response_sum.choices[0].message.content = "Test summary"
        
        mock_create.side_effect = [mock_response_cat, mock_response_sum]
        
        result = ai_service.process_email(sample_email, sample_categories)
        
        assert result["category_id"] == 1
        assert result["summary"] == "Test summary"
        assert mock_create.call_count == 2

