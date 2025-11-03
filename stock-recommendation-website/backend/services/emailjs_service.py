# services/emailjs_service.py
import os
import requests
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class EmailJSService:
    def __init__(self):
        self.emailjs_public_key = os.getenv('EMAILJS_PUBLIC_KEY')
        self.emailjs_service_id = os.getenv('EMAILJS_SERVICE_ID')
        self.base_url = "https://api.emailjs.com/api/v1.0/email/send"
        
        if self._validate_required_config():
            logger.info("✅ EmailJSService initialized with valid configuration")
        else:
            logger.warning("⚠️ EmailJSService missing required configuration")
        
    def _validate_required_config(self) -> bool:
        return bool(self.emailjs_public_key and self.emailjs_service_id)
    
    def send_email(self, to_email: str, template_params: Dict[str, Any]) -> bool:
        try:
            if not self._validate_required_config():
                logger.error("EmailJS configuration incomplete")
                return False
            
            # Ensure to_email is included in template_params
            template_params['to_email'] = to_email
            
            payload = {
                "user_id": self.emailjs_public_key,
                "service_id": self.emailjs_service_id,
                "template_params": template_params
            }
            
            headers = {
                "Content-Type": "application/json",
                "Origin": os.getenv('EMAILJS_ORIGIN', 'https://equibull-production.up.railway.app')
            }
            
            response = requests.post(
                self.base_url,
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Email sent successfully to {to_email}")
                return True
            else:
                logger.error(f"❌ EmailJS API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error sending email via EmailJS: {str(e)}")
            return False

# Singleton instance
emailjs_service = EmailJSService()
