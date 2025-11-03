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
        self.emailjs_public_key = os.getenv('EMAILJS_PUBLIC_KEY')  # Public Key (User ID)
        self.emailjs_service_id = os.getenv('EMAILJS_SERVICE_ID')
        self.emailjs_template_id = os.getenv('EMAILJS_TEMPLATE_ID')  # Optional, can be passed dynamically
        self.emailjs_private_key = os.getenv('EMAILJS_PRIVATE_KEY')  # Optional, for secure requests
        self.base_url = "https://api.emailjs.com/api/v1.0/email/send"
        
        # Log initialization
        logger.info("EmailJSService initialized")
        if not self._validate_required_config():
            logger.warning("EmailJS required configuration is incomplete")
        
    def _validate_required_config(self) -> bool:
        """Validate that required EmailJS configuration is present"""
        required_configs = [
            self.emailjs_public_key,
            self.emailjs_service_id
        ]
        return all(required_configs)
    
    def _validate_template_config(self, template_id: Optional[str] = None) -> bool:
        """Validate that we have a template ID"""
        final_template_id = template_id or self.emailjs_template_id
        return bool(final_template_id)
    
    def send_email(
        self,
        to_email: str,
        template_params: Dict[str, Any],
        template_id: Optional[str] = None,
        service_id: Optional[str] = None
    ) -> bool:
        """
        Send email using EmailJS
        
        Args:
            to_email: Recipient email address
            template_params: Dynamic parameters for the email template
            template_id: Template ID (required if not set in env)
            service_id: Optional service ID (uses default if not provided)
            
        Returns:
            bool: True if email was sent successfully, False otherwise
        """
        try:
            if not self._validate_required_config():
                logger.error("EmailJS configuration is incomplete. Check EMAILJS_PUBLIC_KEY and EMAILJS_SERVICE_ID environment variables")
                return False
            
            if not self._validate_template_config(template_id):
                logger.error("No template_id provided and EMAILJS_TEMPLATE_ID not set in environment")
                return False
            
            # Prepare the payload for EmailJS
            payload = {
                "user_id": self.emailjs_public_key,  # This is the Public Key
                "service_id": service_id or self.emailjs_service_id,
                "template_id": template_id or self.emailjs_template_id,
                "template_params": {
                    "to_email": to_email,
                    **template_params
                }
            }
            
            # Add private key to headers if available (for secure requests)
            headers = {
                "Content-Type": "application/json",
                "Origin": os.getenv('EMAILJS_ORIGIN', 'http://localhost')
            }
            
            if self.emailjs_private_key:
                headers["Authorization"] = f"Bearer {self.emailjs_private_key}"
            
            logger.debug(f"Sending email to {to_email} using template {template_id or self.emailjs_template_id}")
            
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
                
        except requests.exceptions.Timeout:
            logger.error("⏰ EmailJS API request timed out")
            return False
        except requests.exceptions.ConnectionError:
            logger.error("🔌 EmailJS API connection error - check internet connection")
            return False
        except requests.exceptions.RequestException as e:
            logger.error(f"🌐 EmailJS API request error: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"💥 Unexpected error sending email via EmailJS: {str(e)}")
            return False
    
    def send_batch_emails(
        self,
        email_list: List[Dict[str, Any]],
        template_id: Optional[str] = None,
        service_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Send batch emails to multiple recipients
        
        Args:
            email_list: List of dictionaries containing 'to_email' and 'template_params'
            template_id: Optional template ID
            service_id: Optional service ID
            
        Returns:
            Dict with results summary
        """
        results = {
            "successful": 0,
            "failed": 0,
            "errors": [],
            "total": len(email_list)
        }
        
        if not email_list:
            logger.warning("No emails to send in batch")
            return results
        
        logger.info(f"Starting batch email send for {len(email_list)} recipients")
        
        for i, email_data in enumerate(email_list, 1):
            to_email = email_data.get("to_email")
            template_params = email_data.get("template_params", {})
            
            if not to_email:
                results["failed"] += 1
                results["errors"].append(f"Missing email address for recipient #{i}")
                continue
            
            success = self.send_email(
                to_email=to_email,
                template_params=template_params,
                template_id=template_id,
                service_id=service_id
            )
            
            if success:
                results["successful"] += 1
            else:
                results["failed"] += 1
                results["errors"].append(f"Failed to send to {to_email}")
            
            # Log progress for large batches
            if i % 10 == 0 or i == len(email_list):
                logger.info(f"Batch progress: {i}/{len(email_list)} emails processed")
        
        logger.info(f"Batch email send completed: {results['successful']}/{results['total']} successful")
        return results
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test EmailJS connection and configuration
        
        Returns:
            Dict with test results
        """
        test_results = {
            "success": False,
            "config_valid": False,
            "api_accessible": False,
            "errors": []
        }
        
        # Test configuration
        if not self._validate_required_config():
            test_results["errors"].append("Required configuration incomplete - check EMAILJS_PUBLIC_KEY and EMAILJS_SERVICE_ID")
            return test_results
        
        test_results["config_valid"] = True
        
        # Test API accessibility with a simple request
        try:
            test_payload = {
                "user_id": self.emailjs_public_key,
                "service_id": self.emailjs_service_id,
                "template_id": self.emailjs_template_id or "test_template",
                "template_params": {
                    "to_email": "test@example.com",
                    "test_mode": "true"
                }
            }
            
            headers = {
                "Content-Type": "application/json",
                "Origin": os.getenv('EMAILJS_ORIGIN', 'http://localhost')
            }
            
            if self.emailjs_private_key:
                headers["Authorization"] = f"Bearer {self.emailjs_private_key}"
            
            response = requests.post(
                self.base_url,
                json=test_payload,
                headers=headers,
                timeout=10
            )
            
            # Even if it returns an error about template params, the API is accessible
            if response.status_code in [200, 400]:  # 400 might be due to invalid template params
                test_results["api_accessible"] = True
                test_results["success"] = True
                logger.info("✅ EmailJS connection test passed")
            else:
                test_results["errors"].append(f"API returned status code: {response.status_code}")
                logger.warning(f"EmailJS API test returned status: {response.status_code}")
                
        except Exception as e:
            test_results["errors"].append(f"API test failed: {str(e)}")
            logger.error(f"EmailJS connection test failed: {str(e)}")
        
        return test_results
    
    def get_config_status(self) -> Dict[str, bool]:
        """
        Get the status of each configuration parameter
        
        Returns:
            Dict showing which configs are present
        """
        return {
            "EMAILJS_PUBLIC_KEY": bool(self.emailjs_public_key),
            "EMAILJS_SERVICE_ID": bool(self.emailjs_service_id),
            "EMAILJS_TEMPLATE_ID": bool(self.emailjs_template_id),
            "EMAILJS_PRIVATE_KEY": bool(self.emailjs_private_key),
            "REQUIRED_CONFIGS_PRESENT": self._validate_required_config()
        }


# Singleton instance for easy import
emailjs_service = EmailJSService()