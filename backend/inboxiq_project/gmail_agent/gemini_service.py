# backend/inboxiq_project/gmail_agent/gemini_service.py
import google.generativeai as genai
from django.conf import settings
import json
import re
from typing import Dict, List, Optional, Tuple


class GeminiService:
    """Service class for interacting with Google Gemini API"""
    
    def __init__(self):
        # Configure Gemini API - Direct key application
        self.api_key = settings.GEMINI_API_KEY
        
        # Also try to get from environment directly as fallback
        if not self.api_key or self.api_key == 'AIzaSyDKzHLs-bthDsnHIuFVIPwq05ceuqO22FY':
            import os
            self.api_key = os.getenv('GEMINI_API_KEY', 'AIzaSyDKzHLs-bthDsnHIuFVIPwq05ceuqO22FY')
        
        print(f"[GEMINI] API Key configured: {self.api_key[:10]}..." if self.api_key else "[GEMINI] No API key found")
        print(f"[GEMINI] Full API key check: {self.api_key}")
        
        if self.api_key and self.api_key != 'AIzaSyDKzHLs-bthDsnHIuFVIPwq05ceuqO22FY':
            try:
                genai.configure(api_key=self.api_key)
                self.model = genai.GenerativeModel('gemini-2.0-flash')
                self.use_mock = False
                print("[GEMINI] Successfully configured with real API key")
            except Exception as e:
                print(f"[GEMINI] Error configuring API: {e}")
                self.model = None
                self.use_mock = True
        else:
            print("[GEMINI] Using mock responses - configure GEMINI_API_KEY for real AI")
            self.model = None
            self.use_mock = True
        
    def analyze_user_intent(self, message: str) -> Dict:
        """
        Analyze user message to determine intent (normal chat vs email composition)
        Returns: {
            'intent': 'chat' | 'email',
            'recipient_info': str | None,
            'email_context': str | None
        }
        """
        if self.use_mock:
            return self._mock_analyze_intent(message)
        
        prompt = f"""
        Analyze the following user message and determine if they want to:
        1. Have a normal conversation (intent: "chat")
        2. Write/send an email (intent: "email")

        If it's an email intent, extract:
        - Who they want to send the email to (recipient_info)
        - What the email should be about (email_context)

        User message: "{message}"

        Respond in JSON format:
        {{
            "intent": "chat" or "email",
            "recipient_info": "person name or description if email intent, null otherwise",
            "email_context": "what the email should be about if email intent, null otherwise",
            "confidence": 0.0 to 1.0
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            print(f"Error analyzing intent: {e}")
            return {
                'intent': 'chat',
                'recipient_info': None,
                'email_context': None,
                'confidence': 0.0
            }
    
    def generate_chat_response(self, message: str, chat_history: List[Dict] = None) -> str:
        """Generate a normal chat response using Gemini"""
        
        if self.use_mock:
            return self._mock_chat_response(message)
        
        # Build conversation context
        context = "You are InboxIQ, an intelligent email assistant. You help users with general questions and email composition. Be helpful, friendly, and concise.\n\n"
        
        if chat_history:
            context += "Previous conversation:\n"
            for msg in chat_history[-5:]:  # Last 5 messages for context
                role = "User" if msg['message_type'] == 'user' else "Assistant"
                context += f"{role}: {msg['content']}\n"
        
        context += f"\nUser: {message}\nAssistant:"
        
        try:
            response = self.model.generate_content(context)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating chat response: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again."
    
    def generate_email_content(self, recipient_name: str, recipient_email: str, 
                             email_context: str, user_name: str = None) -> Dict:
        """
        Generate email subject and body based on context
        Returns: {
            'subject': str,
            'body': str,
            'tone': str
        }
        """
        
        sender_info = f"from {user_name}" if user_name else "from the user"
        
        prompt = f"""
        Generate a professional email {sender_info} to {recipient_name} ({recipient_email}).
        
        Email context/purpose: {email_context}
        
        Please generate:
        1. An appropriate subject line
        2. A well-structured email body that is professional but friendly
        3. The tone of the email (formal/informal/friendly)
        
        The email should be clear, concise, and appropriate for the context.
        
        Respond in JSON format:
        {{
            "subject": "email subject line",
            "body": "complete email body with proper formatting",
            "tone": "formal/informal/friendly"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            print(f"Error generating email content: {e}")
            return {
                'subject': f"Message for {recipient_name}",
                'body': f"Hi {recipient_name},\n\n{email_context}\n\nBest regards",
                'tone': 'friendly'
            }
    
    def improve_email_content(self, current_subject: str, current_body: str, 
                            improvement_request: str) -> Dict:
        """
        Improve existing email content based on user feedback
        """
        prompt = f"""
        The user wants to improve this email:
        
        Subject: {current_subject}
        Body: {current_body}
        
        User's improvement request: {improvement_request}
        
        Please provide an improved version of the email.
        
        Respond in JSON format:
        {{
            "subject": "improved subject line",
            "body": "improved email body",
            "changes_made": "brief description of what was changed"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return result
        except Exception as e:
            print(f"Error improving email content: {e}")
            return {
                'subject': current_subject,
                'body': current_body,
                'changes_made': 'No changes could be made due to an error.'
            }
    
    def extract_contact_search_terms(self, recipient_info: str) -> List[str]:
        """
        Extract possible search terms for finding contacts
        """
        prompt = f"""
        Extract possible search terms to find a contact from this description: "{recipient_info}"
        
        Consider:
        - Full names
        - First names only
        - Last names only
        - Nicknames
        - Job titles or roles
        - Company names
        
        Return a JSON array of search terms, ordered by likelihood of success:
        ["most_likely_term", "second_term", "third_term", ...]
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = json.loads(response.text.strip())
            return result if isinstance(result, list) else [recipient_info]
        except Exception as e:
            print(f"Error extracting search terms: {e}")
            # Fallback: simple extraction
            terms = [recipient_info.strip()]
            # Add individual words as search terms
            words = recipient_info.split()
            for word in words:
                if len(word) > 2 and word.lower() not in ['the', 'and', 'or', 'to', 'from']:
                    terms.append(word)
            return terms
    
    def _mock_analyze_intent(self, message: str) -> Dict:
        """Mock intent analysis for testing without API key"""
        message_lower = message.lower()
        
        # Simple keyword-based intent detection
        email_keywords = ['send email', 'email', 'write to', 'message', 'mail', 'compose']
        
        if any(keyword in message_lower for keyword in email_keywords):
            # Extract recipient info (simple pattern matching)
            words = message.split()
            recipient_info = None
            email_context = message
            
            # Look for "to [name]" pattern
            if 'to ' in message_lower:
                to_index = message_lower.find('to ')
                after_to = message[to_index + 3:].strip()
                # Get the next few words as recipient
                recipient_words = after_to.split()[:3]  # Take up to 3 words
                recipient_info = ' '.join(recipient_words)
                
                # Remove common words
                for word in ['about', 'regarding', 'concerning']:
                    if word in recipient_info.lower():
                        recipient_info = recipient_info.split(word)[0].strip()
                        break
            
            return {
                'intent': 'email',
                'recipient_info': recipient_info,
                'email_context': email_context,
                'confidence': 0.8
            }
        else:
            return {
                'intent': 'chat',
                'recipient_info': None,
                'email_context': None,
                'confidence': 0.9
            }
    
    def _mock_chat_response(self, message: str) -> str:
        """Mock chat response for testing without API key"""
        message_lower = message.lower()
        
        if 'hello' in message_lower or 'hi' in message_lower:
            return "Hello! I'm InboxIQ, your intelligent email assistant. I can help you with general questions or compose and send emails. How can I assist you today?"
        elif 'help' in message_lower:
            return "I can help you with:\n• General questions and conversations\n• Composing and sending emails\n• Finding contacts in your Gmail\n\nJust tell me what you need!"
        elif 'email' in message_lower:
            return "I'd be happy to help you with email! You can say something like 'Send an email to John about the meeting' and I'll help you compose and send it."
        elif 'thank' in message_lower:
            return "You're welcome! Is there anything else I can help you with?"
        else:
            return "I understand you're asking about that. While I'm running in demo mode (Gemini API not configured), I can still help you compose and send emails. Try saying 'Send an email to [person] about [topic]'!"