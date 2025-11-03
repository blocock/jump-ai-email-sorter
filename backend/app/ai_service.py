from openai import OpenAI
from typing import List, Dict, Optional
from app.config import settings


class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
    
    def categorize_email(self, email_data: Dict, categories: List[Dict]) -> Optional[int]:
        """
        Categorize an email based on available categories
        Returns the category_id or None if no good match
        """
        if not categories:
            return None
        
        # Build prompt
        categories_text = "\n".join([
            f"ID: {cat['id']}, Name: {cat['name']}, Description: {cat['description']}"
            for cat in categories
        ])
        
        email_content = f"""
Subject: {email_data.get('subject', '')}
From: {email_data.get('sender', '')} <{email_data.get('sender_email', '')}>
Body (truncated): {email_data.get('body_text', '')[:1000]}
        """.strip()
        
        prompt = f"""You are an email categorization assistant. Given the following email and list of categories, determine which category best fits this email.

Categories:
{categories_text}

Email:
{email_content}

Respond with ONLY the category ID number that best matches this email. If none of the categories are a good fit, respond with "0".
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an email categorization assistant. Respond only with a category ID number."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=10
            )
            
            category_id_str = response.choices[0].message.content.strip()
            category_id = int(category_id_str)
            
            # Verify it's a valid category
            if category_id == 0:
                return None
            
            valid_ids = [cat['id'] for cat in categories]
            if category_id in valid_ids:
                return category_id
            
            return None
            
        except Exception as e:
            print(f"Error categorizing email: {e}")
            return None
    
    def summarize_email(self, email_data: Dict) -> str:
        """
        Generate an AI summary of an email
        """
        email_content = f"""
Subject: {email_data.get('subject', '')}
From: {email_data.get('sender', '')} <{email_data.get('sender_email', '')}>
Body: {email_data.get('body_text', '')[:3000]}
        """.strip()
        
        prompt = f"""Summarize the following email in 1-2 concise sentences. Focus on the main point or action items.

Email:
{email_content}

Summary:"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are an email summarization assistant. Provide concise, actionable summaries."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )
            
            summary = response.choices[0].message.content.strip()
            return summary
            
        except Exception as e:
            print(f"Error summarizing email: {e}")
            return "Unable to generate summary."
    
    def process_email(self, email_data: Dict, categories: List[Dict]) -> Dict:
        """
        Process an email: categorize and summarize it
        Returns dict with category_id and summary
        """
        category_id = self.categorize_email(email_data, categories)
        summary = self.summarize_email(email_data)
        
        return {
            'category_id': category_id,
            'summary': summary
        }

