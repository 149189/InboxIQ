# gmail_agent/gemini_service.py - Enhanced Version
import json
import re
from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
import hashlib

class GeminiService:
    """
    Enhanced GeminiService with improved email generation capabilities:
    - Template-based email generation with context awareness
    - Better intent classification with confidence scoring
    - Support for different email types (meeting, follow-up, inquiry, etc.)
    - Content personalization based on user preferences
    """

    def __init__(self, model=None, use_mock: bool = True):
        self.model = model
        self.use_mock = use_mock or (model is None)
        self.email_templates = self._load_email_templates()
        print(f"[GEMINI] Enhanced GeminiService initialized; use_mock={self.use_mock}")

    def _load_email_templates(self) -> Dict:
        """Load email templates for different scenarios"""
        return {
            'meeting_request': {
                'subject_patterns': [
                    "Meeting request: {topic}",
                    "Let's discuss {topic}",
                    "Scheduling time to talk about {topic}",
                    "{topic} - Meeting request"
                ],
                'body_templates': [
                    "I hope you're doing well. I'd like to schedule a meeting to discuss {topic}. Would {time} work for you?",
                    "Hi {name}, I hope this email finds you well. I'm reaching out to see if we could set up a meeting about {topic}. Are you available {time}?",
                    "Hello {name}, I'd appreciate the opportunity to discuss {topic} with you. Would you be free for a meeting {time}?"
                ]
            },
            'follow_up': {
                'subject_patterns': [
                    "Following up on {topic}",
                    "Quick follow-up: {topic}",
                    "Checking in about {topic}",
                    "Re: {topic}"
                ],
                'body_templates': [
                    "I wanted to follow up on {topic} that we discussed. Do you have any updates?",
                    "Hi {name}, I hope you're well. I'm checking in regarding {topic}. Please let me know if there's anything you need from my end.",
                    "Just wanted to touch base about {topic}. Is there anything I can help move forward?"
                ]
            },
            'inquiry': {
                'subject_patterns': [
                    "Question about {topic}",
                    "Inquiry: {topic}",
                    "Quick question regarding {topic}",
                    "{topic} - Question"
                ],
                'body_templates': [
                    "I have a question about {topic}. Could you help me understand this better?",
                    "Hi {name}, I hope you're doing well. I have a quick question regarding {topic}. Would you be able to provide some guidance?",
                    "I'd appreciate your insight on {topic}. Do you have a moment to discuss this?"
                ]
            },
            'general': {
                'subject_patterns': [
                    "Regarding {topic}",
                    "About {topic}",
                    "Quick note about {topic}",
                    "{topic}"
                ],
                'body_templates': [
                    "I hope this email finds you well. I wanted to reach out about {topic}.",
                    "Hi {name}, I hope you're doing well. I'm writing regarding {topic}.",
                    "I wanted to get in touch about {topic}. Please let me know your thoughts."
                ]
            }
        }

    def analyze_user_intent(self, message: str) -> Dict:
        """Enhanced intent analysis with email type classification"""
        if not message:
            return {'intent': 'chat', 'recipient_info': None, 'email_context': None, 'confidence': 0.0}

        message_lower = message.lower()
        
        # Enhanced email detection
        email_keywords = [
            'send email', 'email', 'write to', 'message', 'mail', 'compose', 
            'send an email', 'send mail', 'reach out to', 'contact', 'get in touch'
        ]
        
        has_email_intent = any(k in message_lower for k in email_keywords)
        
        if has_email_intent:
            # Classify email type
            email_type = self._classify_email_type(message)
            
            # Extract recipient and context
            recipient_info = self._extract_recipient_info(message)
            email_context = self._extract_email_context(message)
            
            # Calculate confidence based on multiple factors
            confidence = self._calculate_confidence(message, recipient_info, email_context)
            
            return {
                'intent': 'email',
                'email_type': email_type,
                'recipient_info': recipient_info,
                'email_context': email_context,
                'confidence': confidence,
                'extracted_details': self._extract_email_details(message)
            }
        else:
            return {'intent': 'chat', 'recipient_info': None, 'email_context': message, 'confidence': 0.9}

    def _classify_email_type(self, message: str) -> str:
        """Classify the type of email based on content"""
        message_lower = message.lower()
        
        meeting_indicators = ['meeting', 'meet', 'schedule', 'appointment', 'call', 'discuss', 'time to talk']
        follow_up_indicators = ['follow up', 'following up', 'check in', 'update', 'status', 'progress']
        inquiry_indicators = ['question', 'ask', 'help', 'how', 'what', 'why', 'when', 'where', 'clarify']
        
        if any(indicator in message_lower for indicator in meeting_indicators):
            return 'meeting_request'
        elif any(indicator in message_lower for indicator in follow_up_indicators):
            return 'follow_up'
        elif any(indicator in message_lower for indicator in inquiry_indicators):
            return 'inquiry'
        else:
            return 'general'

    def _extract_recipient_info(self, message: str) -> Optional[str]:
        """Enhanced recipient extraction with multiple patterns"""
        patterns = [
            r'\bto\s+([A-Za-z][A-Za-z\s\.-]{1,30})',
            r'\bemail\s+([A-Za-z][A-Za-z\s\.-]{1,30})',
            r'\bmessage\s+([A-Za-z][A-Za-z\s\.-]{1,30})',
            r'\bcontact\s+([A-Za-z][A-Za-z\s\.-]{1,30})',
            r'[\w\.-]+@[\w\.-]+\.\w+',  # Email addresses
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                recipient = match.group(1) if match.lastindex else match.group(0)
                # Clean up common stop words
                cleaned = re.sub(r'\b(about|regarding|for|at|on|tomorrow|today|please)\b.*', '', recipient, flags=re.IGNORECASE).strip()
                if len(cleaned) > 1:
                    return cleaned
        
        return None

    def _extract_email_context(self, message: str) -> str:
        """Extract the main context/topic from the message"""
        # Remove command-like phrases
        context = re.sub(r'\b(send\s+(?:an\s+)?email\s+to|email|message|write\s+to|contact)\s+[A-Za-z\s\.-]*\b', '', message, flags=re.IGNORECASE)
        context = re.sub(r'\b(can\s+you|could\s+you|please|pls)\b', '', context, flags=re.IGNORECASE)
        
        # Look for topic indicators
        topic_match = re.search(r'\b(?:about|regarding|re|for)\s+(.+)', context, re.IGNORECASE)
        if topic_match:
            return topic_match.group(1).strip()
        
        return context.strip()

    def _extract_email_details(self, message: str) -> Dict:
        """Extract specific details like time, urgency, etc."""
        details = {}
        
        # Extract time references
        time_patterns = [
            r'\b(?:at|for)\s+((?:\d{1,2}(?::\d{2})?\s?(?:am|pm)?|\d{1,2}\s?(?:am|pm)))\b',
            r'\b(tomorrow|today|this\s+week|next\s+week|monday|tuesday|wednesday|thursday|friday)\b',
            r'\b(\d{1,2}/\d{1,2}(?:/\d{2,4})?)\b'
        ]
        
        for pattern in time_patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                details['proposed_time'] = match.group(1)
                break
        
        # Extract urgency indicators
        urgency_indicators = ['urgent', 'asap', 'immediately', 'as soon as possible', 'priority']
        if any(indicator in message.lower() for indicator in urgency_indicators):
            details['urgency'] = 'high'
        
        # Extract topic/subject
        topic_match = re.search(r'\b(?:about|regarding|re)\s+([^,.!?]+)', message, re.IGNORECASE)
        if topic_match:
            details['topic'] = topic_match.group(1).strip()
        
        return details

    def _calculate_confidence(self, message: str, recipient_info: Optional[str], email_context: str) -> float:
        """Calculate confidence score for email intent"""
        confidence = 0.5  # Base confidence
        
        # Boost for clear email keywords
        email_keywords = ['send email', 'email', 'compose', 'draft']
        if any(keyword in message.lower() for keyword in email_keywords):
            confidence += 0.2
        
        # Boost for recipient info
        if recipient_info:
            if '@' in recipient_info:  # Email address
                confidence += 0.3
            else:  # Name
                confidence += 0.2
        
        # Boost for clear context
        if email_context and len(email_context.split()) > 2:
            confidence += 0.1
        
        return min(confidence, 1.0)

    def generate_email_variants(
        self,
        recipient_name: str,
        recipient_email: str,
        email_context: str,
        email_type: str = 'general',
        user_name: str = '',
        extracted_details: Dict = None
    ) -> List[Dict]:
        """Generate multiple email variants for the user to choose from"""
        
        extracted_details = extracted_details or {}
        topic = extracted_details.get('topic', email_context)
        proposed_time = extracted_details.get('proposed_time', '')
        
        variants = []
        templates = self.email_templates.get(email_type, self.email_templates['general'])
        
        # Generate 2-3 variants with different tones/styles
        for i in range(min(3, len(templates['body_templates']))):
            subject_template = templates['subject_patterns'][i % len(templates['subject_patterns'])]
            body_template = templates['body_templates'][i]
            
            # Format templates with context
            subject = subject_template.format(
                topic=topic[:50],
                time=proposed_time
            ).strip()
            
            body_parts = []
            
            # Greeting
            greeting = f"Hi {recipient_name.split()[0] if recipient_name else 'there'}," if i == 0 else f"Hello {recipient_name.split()[0] if recipient_name else ''},"
            body_parts.append(greeting)
            body_parts.append("")
            
            # Main content
            main_content = body_template.format(
                name=recipient_name.split()[0] if recipient_name else '',
                topic=topic,
                time=f"at {proposed_time}" if proposed_time else "soon"
            )
            body_parts.append(main_content)
            body_parts.append("")
            
            # Closing based on email type and variant
            if email_type == 'meeting_request':
                closings = [
                    "Please let me know what works best for you.",
                    "I look forward to hearing from you.",
                    "Would you be able to let me know your availability?"
                ]
            elif email_type == 'follow_up':
                closings = [
                    "Thanks for your time and consideration.",
                    "I appreciate any updates you can share.",
                    "Please let me know if you need anything from my end."
                ]
            else:
                closings = [
                    "Thank you for your time.",
                    "I appreciate your help with this.",
                    "Looking forward to your response."
                ]
            
            body_parts.append(closings[i % len(closings)])
            body_parts.append("")
            body_parts.append("Best regards,")
            body_parts.append(user_name or "")
            
            variants.append({
                'variant_id': i + 1,
                'subject': subject,
                'body': '\n'.join(body_parts),
                'tone': ['professional', 'friendly', 'concise'][i],
                'style_description': ['Formal and professional', 'Warm and friendly', 'Direct and concise'][i]
            })
        
        return variants

    def generate_email_content(
        self,
        recipient_name: str,
        recipient_email: str,
        email_context: str,
        user_name: str,
        tone: str = "professional",
        length: str = "short",
        email_type: str = "general",
        extracted_details: Dict = None
    ) -> Dict:
        """
        Enhanced email generation that returns multiple variants
        """
        # If we have a model and mock is disabled, try AI generation first
        if not self.use_mock and self.model:
            try:
                ai_result = self._generate_with_ai_model(
                    recipient_name, recipient_email, email_context, 
                    user_name, tone, length, email_type, extracted_details
                )
                if ai_result:
                    return ai_result
            except Exception as e:
                print(f"[GEMINI] AI generation failed: {e}, falling back to templates")
        
        # Generate template-based variants
        variants = self.generate_email_variants(
            recipient_name, recipient_email, email_context, 
            email_type, user_name, extracted_details
        )
        
        # Return the first variant as primary, but include all variants
        primary_variant = variants[0] if variants else self._generate_fallback_email(
            recipient_name, recipient_email, email_context, user_name
        )
        
        return {
            'subject': primary_variant['subject'],
            'body': primary_variant['body'],
            'variants': variants,
            'email_type': email_type,
            'generated_at': datetime.now().isoformat()
        }

    def _generate_with_ai_model(self, recipient_name, recipient_email, email_context, user_name, tone, length, email_type, extracted_details):
        """Use AI model for email generation with better prompting"""
        extracted_details = extracted_details or {}
        
        prompt = f"""
Generate a professional email with the following details:
- Recipient: {recipient_name} ({recipient_email})
- Context: {email_context}
- Type: {email_type}
- Tone: {tone}
- Length: {length}
- Sender: {user_name}
- Additional details: {json.dumps(extracted_details)}

Requirements:
1. Return valid JSON with "subject" and "body" fields
2. Subject should be concise and specific
3. Body should include proper greeting, main content, and professional closing
4. Avoid echoing the user's raw instruction
5. Make it natural and contextually appropriate

Example output:
{{"subject": "Meeting request: Project discussion", "body": "Hi John,\\n\\nI hope you're doing well. I'd like to schedule a meeting to discuss the project timeline. Would Tuesday at 2 PM work for you?\\n\\nPlease let me know your availability.\\n\\nBest regards,\\nSarah"}}
"""
        
        response = self.model.generate_content(prompt)
        text = (response.text or "").strip()
        
        try:
            parsed = json.loads(text)
            if 'subject' in parsed and 'body' in parsed:
                return {
                    'subject': parsed['subject'],
                    'body': parsed['body'],
                    'variants': [parsed],  # Single AI-generated variant
                    'email_type': email_type,
                    'generated_at': datetime.now().isoformat()
                }
        except json.JSONDecodeError:
            pass
        
        return None

    def _generate_fallback_email(self, recipient_name, recipient_email, email_context, user_name):
        """Generate a simple fallback email when all else fails"""
        subject = f"Regarding: {email_context[:50]}" if email_context else "Quick note"
        
        body = f"""Hi {recipient_name.split()[0] if recipient_name else 'there'},

I hope this email finds you well. {email_context}

Please let me know your thoughts.

Best regards,
{user_name or ''}"""
        
        return {
            'subject': subject,
            'body': body,
            'tone': 'professional',
            'style_description': 'Simple and direct'
        }

    # Keep existing methods for backward compatibility
    def extract_contact_search_terms(self, recipient_info: Optional[str]) -> List[str]:
        """Enhanced contact search term extraction"""
        if not recipient_info:
            return []

        recipient_info = str(recipient_info).strip()
        if not recipient_info:
            return []

        # If it's an email, return as-is
        if re.match(r'[^@]+@[^@]+\.[^@]+', recipient_info):
            return [recipient_info]

        terms = []
        
        # Add full name/term
        terms.append(recipient_info)
        
        # Split into words and add meaningful ones
        words = recipient_info.split()
        for word in words:
            if len(word) > 2 and word.lower() not in ['the', 'and', 'or', 'to', 'from', 'for', 'with', 'about']:
                terms.append(word)
        
        # Add first and last name combinations
        if len(words) >= 2:
            terms.append(words[0])  # First name
            terms.append(words[-1])  # Last name
            terms.append(f"{words[0]} {words[-1]}")  # First + Last
        
        # Deduplicate while preserving order
        seen = set()
        dedup_terms = []
        for term in terms:
            key = term.strip().lower()
            if key and key not in seen:
                seen.add(key)
                dedup_terms.append(term.strip())
        
        return dedup_terms[:5]  # Limit to top 5 terms

    def generate_chat_response(self, message: str, chat_history: List[Dict]) -> str:
        """Generate contextual chat responses"""
        if self.use_mock:
            # Enhanced mock responses based on context
            message_lower = message.lower()
            
            if any(word in message_lower for word in ['hello', 'hi', 'hey']):
                return "Hello! I'm here to help you with emails and general questions. What would you like to do today?"
            elif any(word in message_lower for word in ['help', 'what can you do']):
                return "I can help you compose professional emails, manage your contacts, and answer general questions. Try saying 'Send an email to [name] about [topic]' to get started!"
            elif 'thank' in message_lower:
                return "You're welcome! Is there anything else I can help you with?"
            else:
                return f"I understand you mentioned: \"{message[:100]}{'...' if len(message) > 100 else ''}\" - How can I help you with that?"
        
        try:
            # Use AI model for more sophisticated responses
            context = " ".join([f"{msg['message_type']}: {msg['content']}" for msg in chat_history[-3:]])
            prompt = f"Context: {context}\nUser: {message}\nRespond helpfully as an email assistant:"
            
            response = self.model.generate_content(prompt)
            return (response.text or "").strip()[:500]  # Limit response length
        except Exception as e:
            print(f"[GEMINI] Chat response error: {e}")
            return "I'm sorry, I encountered an issue processing your message. How can I help you?"