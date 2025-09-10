# backend/inboxiq_project/gmail_agent/gmail_service.py
import base64
import json
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
from typing import Dict, Optional


class GmailServiceError(Exception):
    """Raised when Gmail API returns an error response."""


class GmailService:
    """Service for interacting with Gmail API"""

    def __init__(self, access_token: str):
        self.access_token = access_token
        self.base_url = "https://gmail.googleapis.com/gmail/v1"
        self.headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        }

    # ---------------------------
    # Internal HTTP helper
    # ---------------------------
    def _request(self, method: str, url: str, **kwargs) -> Dict:
        try:
            response = requests.request(method, url, headers=self.headers, **kwargs)
            if response.status_code in (200, 204):
                if response.status_code == 204:
                    return {}
                return response.json()
            else:
                # Raise with details so caller can catch & log
                raise GmailServiceError(
                    f"Gmail API {method} {url} failed: "
                    f"{response.status_code} - {response.text}"
                )
        except requests.RequestException as e:
            raise GmailServiceError(f"Request error: {e}")

    # ---------------------------
    # Drafts
    # ---------------------------
    def create_draft(
        self, to_email: str, subject: str, body: str, from_email: str = None
    ) -> str:
        """Create a draft email in Gmail. Returns draft ID if successful."""
        message = MIMEMultipart()
        message["to"] = to_email
        message["subject"] = subject
        if from_email:
            message["from"] = from_email
        message.attach(MIMEText(body, "plain"))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        url = f"{self.base_url}/users/me/drafts"
        draft_data = {"message": {"raw": raw_message}}

        res = self._request("POST", url, json=draft_data)
        return res.get("id")

    def send_draft(self, draft_id: str) -> str:
        """Send a draft email. Returns message ID if successful."""
        url = f"{self.base_url}/users/me/drafts/{draft_id}/send"
        res = self._request("POST", url)
        return res.get("id")

    def delete_draft(self, draft_id: str) -> bool:
        """Delete a draft email. Returns True if deleted."""
        url = f"{self.base_url}/users/me/drafts/{draft_id}"
        self._request("DELETE", url)
        return True

    def update_draft(
        self, draft_id: str, to_email: str, subject: str, body: str, from_email: str = None
    ) -> str:
        """Replace an existing draft with new content. Returns new draft ID."""
        self.delete_draft(draft_id)
        return self.create_draft(to_email, subject, body, from_email)

    # ---------------------------
    # Direct send
    # ---------------------------
    def send_email_directly(
        self, to_email: str, subject: str, body: str, from_email: str = None
    ) -> str:
        """Send an email directly without creating a draft first. Returns message ID."""
        message = MIMEMultipart()
        message["to"] = to_email
        message["subject"] = subject
        if from_email:
            message["from"] = from_email
        message.attach(MIMEText(body, "plain"))

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode("utf-8")

        url = f"{self.base_url}/users/me/messages/send"
        message_data = {"raw": raw_message}

        res = self._request("POST", url, json=message_data)
        return res.get("id")

    # ---------------------------
    # Profile
    # ---------------------------
    def get_user_profile(self) -> Optional[Dict]:
        """Get Gmail user profile information"""
        url = f"{self.base_url}/users/me/profile"
        try:
            return self._request("GET", url)
        except GmailServiceError as e:
            print(f"[GmailService] Error getting profile: {e}")
            return None
