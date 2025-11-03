# services/emailjs_service.py
import os
import requests
import logging
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)

class EmailJSService:
    """
    Service for handling email operations using EmailJS API
    """
    
    def __init__(self):
        self.emailjs_public_key = os.getenv('EMAILJS_PUBLIC_KEY')
        self.emailjs_service_id = os.getenv('EMAILJS_SERVICE_ID')
        self.base_url = "https://api.emailjs.com/api/v1.0/email/send"
        
        # Log configuration status
        if self._validate_required_config():
            logger.info("✅ EmailJSService initialized with valid configuration")
        else:
            logger.warning("⚠️ EmailJSService initialized but missing required configuration")
            logger.warning("   Set EMAILJS_PUBLIC_KEY and EMAILJS_SERVICE_ID in Railway environment variables")
        
    def _validate_required_config(self) -> bool:
        """Validate that required EmailJS configuration is present"""
        return bool(self.emailjs_public_key and self.emailjs_service_id)
    
    def send_email(
        self,
        to_email: str,
        template_params: Dict[str, Any],
        template_id: Optional[str] = None
    ) -> bool:
        """
        Send email using EmailJS
        
        Args:
            to_email: Recipient email address
            template_params: Dynamic parameters for the email template
            template_id: Template ID (optional)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            if not self._validate_required_config():
                logger.error("EmailJS configuration is incomplete. Set EMAILJS_PUBLIC_KEY and EMAILJS_SERVICE_ID in Railway environment variables")
                return False
            
            # Prepare the payload for EmailJS
            payload = {
                "user_id": self.emailjs_public_key,
                "service_id": self.emailjs_service_id,
                "template_params": {
                    "to_email": to_email,
                    **template_params
                }
            }
            
            # Add template_id only if provided
            if template_id:
                payload["template_id"] = template_id
            
            headers = {
                "Content-Type": "application/json",
                "Origin": os.getenv('EMAILJS_ORIGIN', 'https://equibull-production.up.railway.app')
            }
            
            logger.info(f"Sending email to {to_email}")
            
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

    def send_batch_emails(
        self,
        email_list: List[Dict[str, Any]],
        template_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send batch emails to multiple recipients"""
        results = {
            "successful": 0,
            "failed": 0,
            "errors": [],
            "total": len(email_list)
        }
        
        for email_data in email_list:
            success = self.send_email(
                to_email=email_data["to_email"],
                template_params=email_data["template_params"],
                template_id=template_id
            )
            
            if success:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"Failed to send to {email_data['to_email']}")
        
        return results

    def test_connection(self) -> Dict[str, Any]:
        """Test EmailJS connection and configuration"""
        return {
            "success": self._validate_required_config(),
            "config_valid": self._validate_required_config(),
            "public_key_set": bool(self.emailjs_public_key),
            "service_id_set": bool(self.emailjs_service_id)
        }


# Singleton instance
emailjs_service = EmailJSService()
