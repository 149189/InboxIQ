# gmail_agent/gemini_service.py
import json
import re
from typing import List, Optional, Dict

class GeminiService:
    """
    Lightweight wrapper around a (real or mock) Gemini-like model.
    - If GEMINI API is unavailable, runs in mock mode.
    - Provides helpers used by views: analyze_user_intent, extract_contact_search_terms,
      generate_email_content, generate_chat_response.
    """

    def __init__(self, model=None, use_mock=True):
        """
        model: optional real model client object with .generate_content(prompt) -> {text: ...}
        use_mock: force mock behavior if True
        """
        self.model = model
        self.use_mock = use_mock or (model is None)
        print(f"[GEMINI] Initialized GeminiService; use_mock={self.use_mock}, model_present={bool(self.model)}")

    # -------------------
    # Intent analysis
    # -------------------
    def analyze_user_intent(self, message: str) -> Dict:
        """
        Return structure:
        {
            'intent': 'email'|'chat',
            'recipient_info': Optional[str],
            'email_context': Optional[str],
            'confidence': float
        }
        """
        if not message:
            return {'intent': 'chat', 'recipient_info': None, 'email_context': None, 'confidence': 0.0}

        if self.use_mock:
            return self._mock_analyze_intent(message)

        # Real model path (best-effort)
        try:
            prompt = f"""
            Analyze the user's message and detect whether they intend to send an email.
            If yes, extract the recipient hint (name or email) and return a JSON object like:
            {{
              "intent": "email",
              "recipient_info": "recipient hint or email or null",
              "email_context": "the original message or a cleaned version",
              "confidence": 0.9
            }}
            Otherwise return:
            {{
              "intent": "chat",
              "recipient_info": null,
              "email_context": null,
              "confidence": 0.9
            }}
            Message: \"\"\"{message}\"\"\"
            """
            resp = self.model.generate_content(prompt)
            text = (resp.text or "").strip()
            parsed = json.loads(text)
            return parsed
        except Exception as e:
            print(f"[GEMINI] analyze_user_intent model error: {e}")
            return self._mock_analyze_intent(message)

    def _mock_analyze_intent(self, message: str) -> Dict:
        """Simple rule-based detection for testing."""
        message_lower = message.lower()

        email_keywords = ['send email', 'email', 'write to', 'message', 'mail', 'compose', 'send an email', 'send mail', 'send']
        if any(k in message_lower for k in email_keywords):
            recipient_info = None
            email_context = message.strip()

            # Try "to <name>" pattern
            if ' to ' in message_lower:
                try:
                    idx = message_lower.find(' to ')
                    after = message[idx + 4:].strip()
                    # avoid trailing context words
                    stop_words = [' for ', ' about ', ' regarding ', ' at ', ' on ', ' tomorrow', ' today', ' at ']
                    for sw in stop_words:
                        if sw in after.lower():
                            after = after.lower().split(sw)[0].strip()
                            break
                    recipient_info = ' '.join(after.split()[:4]).strip()
                except Exception:
                    recipient_info = None

            # If still none, try "mail <name>" or "email <name>"
            if not recipient_info:
                m = re.search(r'\b(?:mail|email|message|send)\s+to\s+([A-Za-z][A-Za-z\.\-]*(?:\s+[A-Za-z][A-Za-z\.\-]*){0,4})', message, re.I)
                if m:
                    recipient_info = m.group(1).strip()
                else:
                    m2 = re.search(r'\b(?:mail|email|message|send)\s+([A-Za-z][A-Za-z\.\-]*(?:\s+[A-Za-z][A-Za-z\.\-]*){0,4})', message, re.I)
                    if m2:
                        recipient_info = m2.group(1).strip()

            # Last attempt: if the message contains an email address
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)
            if email_match:
                recipient_info = email_match.group(0)

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
                'email_context': message,
                'confidence': 0.9
            }

    # -------------------
    # Extract contact search terms
    # -------------------
    def extract_contact_search_terms(self, recipient_info: Optional[str]) -> List[str]:
        """
        Given recipient_info (may be None), return an ordered list of search terms.
        Defensive: never calls model if self.use_mock or recipient_info falsy.
        """
        if not recipient_info:
            print("[GEMINI] extract_contact_search_terms: recipient_info is empty/falsy")
            return []

        recipient_info = str(recipient_info).strip()
        if not recipient_info:
            return []

        # If looks like email address, return it directly
        if re.match(r'[^@]+@[^@]+\.[^@]+', recipient_info):
            return [recipient_info]

        # Mock/simple path
        if self.use_mock or not self.model:
            terms = []
            terms.append(recipient_info)
            words = recipient_info.split()
            if len(words) >= 1:
                terms.append(words[0])
            if len(words) >= 2:
                terms.append(words[-1])
            for w in words:
                if len(w) > 2 and w.lower() not in ['the', 'and', 'or', 'to', 'from', 'for', 'with']:
                    terms.append(w)
            # dedupe preserving order
            seen = set()
            deduped = []
            for t in terms:
                key = t.strip().lower()
                if key and key not in seen:
                    seen.add(key)
                    deduped.append(t.strip())
            print(f"[GEMINI] Mock contact search terms: {deduped}")
            return deduped

        # Real model path (best-effort)
        try:
            prompt = f"""
            From this description: "{recipient_info}"
            return a JSON array of search terms (names, first name, last name, nicknames, emails)
            Example: ["Full Name", "FirstName", "LastName", "email@example.com"]
            """
            resp = self.model.generate_content(prompt)
            text = (resp.text or "").strip()
            parsed = json.loads(text)
            if isinstance(parsed, list):
                return [str(p).strip() for p in parsed if str(p).strip()]
            else:
                return [recipient_info]
        except Exception as e:
            print(f"[GEMINI] Error extracting contact search terms via model: {e}")
            # fallback to simple split extraction
            try:
                terms = [recipient_info]
                words = recipient_info.split()
                for w in words:
                    if len(w) > 2:
                        terms.append(w)
                seen = set(); res = []
                for t in terms:
                    key = t.strip().lower()
                    if key and key not in seen:
                        seen.add(key); res.append(t.strip())
                return res
            except Exception as e2:
                print(f"[GEMINI] Final fallback in extract_contact_search_terms failed: {e2}")
                return [recipient_info]

    # -------------------
    # Generate email content
    # -------------------
    def generate_email_content(self, recipient_name: str, recipient_email: str, email_context: str, user_name: str) -> Dict:
        """
        Returns: {'subject': str, 'body': str}
        Works in mock mode too.
        """
        if not email_context:
            email_context = ""

        if self.use_mock:
            # Simple mock composer: create a polite subject and body using templates
            subject = f"Regarding: {email_context.split(' for ')[-1][:40].strip() or 'Quick note'}"
            body_lines = []
            body_lines.append(f"Hi {recipient_name or ''},".strip())
            body_lines.append("")
            body_lines.append(email_context.strip())
            body_lines.append("")
            body_lines.append("Best,")
            body_lines.append(user_name or "")
            body = "\n".join([l for l in body_lines if l is not None])
            return {'subject': subject, 'body': body}

        # Real model path
        try:
            prompt = f"""
            Compose a short professional email to {recipient_name} <{recipient_email}> from {user_name}.
            Context / request: {email_context}

            Return a JSON object:
            {{
              "subject": "...",
              "body": "..."
            }}
            """
            resp = self.model.generate_content(prompt)
            parsed = json.loads(resp.text)
            return {
                'subject': parsed.get('subject', '') if isinstance(parsed, dict) else '',
                'body': parsed.get('body', '') if isinstance(parsed, dict) else str(parsed)
            }
        except Exception as e:
            print(f"[GEMINI] generate_email_content error: {e}")
            # fallback
            return {
                'subject': f"Note from {user_name}",
                'body': f"Hi {recipient_name or ''},\n\n{email_context}\n\nBest,\n{user_name}"
            }

    # -------------------
    # Chat response generator
    # -------------------
    def generate_chat_response(self, message: str, chat_history: List[Dict]) -> str:
        if self.use_mock:
            # Echo / simple helpful response
            return f"I understood: \"{message}\" — how can I help with that?"
        try:
            prompt = f"User said: {message}\nChat history: {chat_history}\nReply succinctly."
            resp = self.model.generate_content(prompt)
            return (resp.text or "").strip()
        except Exception as e:
            print(f"[GEMINI] generate_chat_response error: {e}")
            return f"Sorry, I couldn't process that due to an internal error."

