# backend/inboxiq_project/gmail_agent/gmail_service.py
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from typing import Dict, Optional


class GmailService:
    """Service for interacting with Gmail API"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://gmail.googleapis.com/gmail/v1"
        self.headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
    
    def create_draft(self, to_email: str, subject: str, body: str, 
                    from_email: str = None) -> Optional[str]:
        """
        Create a draft email in Gmail
        Returns draft ID if successful
        """
        try:
            # Create the email message
            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = subject
            if from_email:
                message['from'] = from_email
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            # Create draft via API
            url = f"{self.base_url}/users/me/drafts"
            draft_data = {
                'message': {
                    'raw': raw_message
                }
            }
            
            response = requests.post(url, headers=self.headers, json=draft_data)
            
            if response.status_code == 200:
                draft_info = response.json()
                return draft_info.get('id')
            else:
                print(f"Error creating draft: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error creating draft: {e}")
            return None
    
    def send_draft(self, draft_id: str) -> Optional[str]:
        """
        Send a draft email
        Returns message ID if successful
        """
        try:
            url = f"{self.base_url}/users/me/drafts/{draft_id}/send"
            
            response = requests.post(url, headers=self.headers)
            
            if response.status_code == 200:
                message_info = response.json()
                return message_info.get('id')
            else:
                print(f"Error sending draft: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error sending draft: {e}")
            return None
    
    def send_email_directly(self, to_email: str, subject: str, body: str,
                          from_email: str = None) -> Optional[str]:
        """
        Send an email directly without creating a draft first
        Returns message ID if successful
        """
        try:
            # Create the email message
            message = MIMEMultipart()
            message['to'] = to_email
            message['subject'] = subject
            if from_email:
                message['from'] = from_email
            
            # Add body
            message.attach(MIMEText(body, 'plain'))
            
            # Encode the message
            raw_message = base64.urlsafe_b64encode(
                message.as_bytes()
            ).decode('utf-8')
            
            # Send via API
            url = f"{self.base_url}/users/me/messages/send"
            message_data = {
                'raw': raw_message
            }
            
            response = requests.post(url, headers=self.headers, json=message_data)
            
            if response.status_code == 200:
                message_info = response.json()
                return message_info.get('id')
            else:
                print(f"Error sending email: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error sending email: {e}")
            return None
    
    def delete_draft(self, draft_id: str) -> bool:
        """Delete a draft email"""
        try:
            url = f"{self.base_url}/users/me/drafts/{draft_id}"
            
            response = requests.delete(url, headers=self.headers)
            
            return response.status_code == 204
            
        except Exception as e:
            print(f"Error deleting draft: {e}")
            return False
    
    def get_user_profile(self) -> Optional[Dict]:
        """Get Gmail user profile information"""
        try:
            url = f"{self.base_url}/users/me/profile"
            
            response = requests.get(url, headers=self.headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Error getting profile: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            print(f"Error getting profile: {e}")
            return None
    
    def update_draft(self, draft_id: str, to_email: str, subject: str, body: str,
                    from_email: str = None) -> bool:
        """Update an existing draft"""
        try:
            # Delete old draft
            self.delete_draft(draft_id)
            
            # Create new draft with updated content
            new_draft_id = self.create_draft(to_email, subject, body, from_email)
            
            return new_draft_id is not None
            
        except Exception as e:
            print(f"Error updating draft: {e}")
            return False