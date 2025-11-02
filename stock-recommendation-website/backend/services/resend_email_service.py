# services/resend_email_service.py
import os
import logging
import requests
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class ResendEmailService:
    def __init__(self):
        self.api_key = os.getenv('RESEND_API_KEY')
        self.from_email = os.getenv('RESEND_FROM_EMAIL', 'Stock Alerts <onboarding@resend.dev>')
        logger.info(f"📧 Resend service initialized: API key present = {bool(self.api_key)}")
    
    def send_email(self, to_email: str, subject: str, html_content: str) -> bool:
        """Send email via Resend API"""
        try:
            if not self.api_key:
                logger.error("❌ Resend API key not configured")
                return False
            
            logger.info(f"🔄 Sending email to {to_email} via Resend")
            
            response = requests.post(
                'https://api.resend.com/emails',
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'from': self.from_email,
                    'to': [to_email],
                    'subject': subject,
                    'html': html_content
                },
                timeout=10
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Email successfully sent to {to_email} via Resend")
                return True
            else:
                logger.error(f"❌ Resend API error {response.status_code}: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"❌ Resend email error: {e}")
            return False