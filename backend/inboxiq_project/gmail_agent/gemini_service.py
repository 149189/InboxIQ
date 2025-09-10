# gmail_agent/gemini_service.py
import json
import re
from typing import List, Optional, Dict

class GeminiService:
    """
    GeminiService: wrapper around a model client or a mock fallback.
    - If `model` is provided and `use_mock` is False, the service will ask the model
      to produce a JSON object with {"subject": "...", "body": "..."} for emails.
    - If `use_mock` is True or no model is provided, a local generator will create a
      decent email without echoing the user's raw prompt.
    """

    def __init__(self, model=None, use_mock: bool = True):
        """
        model: object expected to implement .generate_content(prompt: str) -> { text: str }
               (adjust to your real Gemini client interface)
        use_mock: force mock mode if True. If False and model is provided, model will be used.
        """
        self.model = model
        self.use_mock = use_mock or (model is None)
        print(f"[GEMINI] Initialized GeminiService; use_mock={self.use_mock}, model_present={bool(self.model)}")

    # -------------------
    # Intent analysis (unchanged mock-friendly)
    # -------------------
    def analyze_user_intent(self, message: str) -> Dict:
        if not message:
            return {'intent': 'chat', 'recipient_info': None, 'email_context': None, 'confidence': 0.0}

        if self.use_mock:
            return self._mock_analyze_intent(message)

        try:
            prompt = f"""
            Analyze the user's message and detect whether they intend to send an email.
            If yes, extract the recipient hint (name or email) and return exactly a JSON object like:
            {{ "intent":"email", "recipient_info":"...", "email_context":"...", "confidence":0.95 }}
            Otherwise return: {{ "intent":"chat", "recipient_info": null, "email_context": null, "confidence":0.9 }}
            Message: \"\"\"{message}\"\"\"
            """
            resp = self.model.generate_content(prompt)
            parsed = json.loads((resp.text or "").strip())
            return parsed
        except Exception as e:
            print(f"[GEMINI] analyze_user_intent model error: {e}")
            return self._mock_analyze_intent(message)

    def _mock_analyze_intent(self, message: str) -> Dict:
        message_lower = message.lower()
        email_keywords = ['send email', 'email', 'write to', 'message', 'mail', 'compose', 'send an email', 'send mail', 'send']
        if any(k in message_lower for k in email_keywords):
            recipient_info = None
            email_context = message.strip()

            # heuristic "to <name>"
            if ' to ' in message_lower:
                try:
                    idx = message_lower.find(' to ')
                    after = message[idx + 4:].strip()
                    stop_words = [' for ', ' about ', ' regarding ', ' at ', ' on ', ' tomorrow', ' today', ' at ']
                    for sw in stop_words:
                        if sw in after.lower():
                            after = after.lower().split(sw)[0].strip()
                            break
                    recipient_info = ' '.join(after.split()[:4]).strip()
                except Exception:
                    recipient_info = None

            # fallback patterns
            if not recipient_info:
                m = re.search(r'\b(?:mail|email|message|send)\s+to\s+([A-Za-z][A-Za-z\.\-]*(?:\s+[A-Za-z][A-Za-z\.\-]*){0,4})', message, re.I)
                if m:
                    recipient_info = m.group(1).strip()
                else:
                    m2 = re.search(r'\b(?:mail|email|message|send)\s+([A-Za-z][A-Za-z\.\-]*(?:\s+[A-Za-z][A-Za-z\.\-]*){0,4})', message, re.I)
                    if m2:
                        recipient_info = m2.group(1).strip()

            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', message)
            if email_match:
                recipient_info = email_match.group(0)

            return {'intent': 'email', 'recipient_info': recipient_info, 'email_context': email_context, 'confidence': 0.8}
        else:
            return {'intent': 'chat', 'recipient_info': None, 'email_context': message, 'confidence': 0.9}

    # -------------------
    # Contact search term helper
    # -------------------
    def extract_contact_search_terms(self, recipient_info: Optional[str]) -> List[str]:
        if not recipient_info:
            print("[GEMINI] extract_contact_search_terms: recipient_info falsy")
            return []

        recipient_info = str(recipient_info).strip()
        if not recipient_info:
            return []

        if re.match(r'[^@]+@[^@]+\.[^@]+', recipient_info):
            return [recipient_info]

        if self.use_mock or not self.model:
            terms = [recipient_info]
            words = recipient_info.split()
            if words:
                terms.append(words[0])
            if len(words) > 1:
                terms.append(words[-1])
            for w in words:
                if len(w) > 2 and w.lower() not in ['the', 'and', 'or', 'to', 'from', 'for', 'with']:
                    terms.append(w)
            seen = set(); dedup = []
            for t in terms:
                k = t.strip().lower()
                if k and k not in seen:
                    seen.add(k); dedup.append(t.strip())
            print(f"[GEMINI] Mock contact search terms: {dedup}")
            return dedup

        try:
            prompt = f"""
            From this description: "{recipient_info}"
            return a JSON array of search terms (names, first name, last name, nicknames, emails).
            Example: ["Full Name", "FirstName", "LastName", "email@example.com"]
            """
            resp = self.model.generate_content(prompt)
            parsed = json.loads((resp.text or "").strip())
            if isinstance(parsed, list):
                return [str(p).strip() for p in parsed if str(p).strip()]
            return [recipient_info]
        except Exception as e:
            print(f"[GEMINI] Error extracting contact search terms: {e}")
            words = recipient_info.split()
            terms = [recipient_info] + [w for w in words if len(w) > 2]
            seen = set(); res = []
            for t in terms:
                k = t.strip().lower()
                if k and k not in seen:
                    seen.add(k); res.append(t.strip())
            return res

    # -------------------
    # Email composition: use model when available for dynamic, natural email generation
    # -------------------
    def generate_email_content(
        self,
        recipient_name: str,
        recipient_email: str,
        email_context: str,
        user_name: str,
        tone: str = "professional",
        length: str = "short"
    ) -> Dict:
        """
        Returns dict {'subject': str, 'body': str}
        If a model is available (self.use_mock == False and self.model), we ask the model to produce JSON.
        Otherwise produce a high-quality local draft (mock) that avoids echoing prompts.
        `tone` may be 'professional'|'casual' etc. `length` may be 'short'|'medium'.
        """
        # Normalize inputs
        email_context = (email_context or "").strip()
        recipient_name = (recipient_name or "").strip()
        recipient_email = (recipient_email or "").strip()
        user_name = user_name or ""

        # helper to clean the user prompt so model doesn't echo prompts
        def _clean_context(ctx: str) -> str:
            c = ctx.strip()
            c = re.sub(r'\b(can you|could you|please|pls|send (an )?email to|send mail to|send to|email to|mail to)\b', '', c, flags=re.I)
            c = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', c)
            c = re.sub(r'\s+', ' ', c).strip()
            return c

        cleaned = _clean_context(email_context)

        # quick extraction helpers
        time_match = re.search(r'\b(?:at|for)\s+((?:\d{1,2}(:\d{2})?\s?(?:am|pm)?|\d{1,2}\s?(?:am|pm)))\b', email_context, re.I)
        meeting_time = time_match.group(1).strip() if time_match else None

        m_topic = re.search(r'\b(?:for|about|regarding|re)\s+(.+)$', email_context, re.I)
        topic = None
        if m_topic:
            topic = m_topic.group(1).strip()
            if meeting_time and meeting_time.lower() in topic.lower():
                topic = re.sub(re.escape(meeting_time), '', topic, flags=re.I).strip()
            topic = re.sub(r'\b(please|tomorrow|today|now)\b', '', topic, flags=re.I).strip()
        else:
            if cleaned and len(cleaned.split()) <= 14:
                topic = cleaned

        # If we have a model and mock is disabled, ask the model for a JSON email
        if not self.use_mock and self.model:
            try:
                # Build a clear instruction prompt that requests JSON only
                model_prompt = f"""
You are an expert assistant that composes concise, professional emails. Produce a JSON object with exactly two fields: "subject" and "body".
- subject: one-line subject (no newlines), 30-80 characters.
- body: full email body including greeting, 1-3 short paragraphs, a clear call-to-action, and a closing/signature.
Requirements:
- Do NOT echo the user's raw instruction like "send mail to ...".
- Avoid including raw email addresses in the body; use greetings and names instead.
- Keep tone: {tone}. Length: {length}.
Input details:
recipient_name: "{recipient_name}"
recipient_email: "{recipient_email}"
user_name: "{user_name}"
meeting_time: "{meeting_time or ''}"
topic: "{topic or ''}"
cleaned_context: "{cleaned}"
Example output:
{{ "subject": "Meeting about X", "body": "Hi Name,\\n\\n...\\n\\nBest,\\nUser" }}
Produce only valid JSON.
"""
                resp = self.model.generate_content(model_prompt)
                text = (resp.text or "").strip()

                # First try strict JSON parse
                try:
                    parsed = json.loads(text)
                    subj = parsed.get('subject', '').strip()
                    body = parsed.get('body', '').strip()
                    if subj and body:
                        return {'subject': subj, 'body': body}
                except Exception:
                    # Not strict JSON — try to extract subject/body heuristically
                    pass

                # Heuristic extraction: look for Subject: and Body separators
                subj = ""
                body = ""
                # common pattern: {"subject": "...", "body": "..."}
                m_json_like = re.search(r'(\{.*\})', text, re.S)
                if m_json_like:
                    try:
                        parsed2 = json.loads(m_json_like.group(1))
                        subj = parsed2.get('subject', '').strip()
                        body = parsed2.get('body', '').strip()
                        if subj and body:
                            return {'subject': subj, 'body': body}
                    except Exception:
                        pass

                # fallback parse: Subject: ... \n\n body...
                m_sub = re.search(r'Subject:\s*(.+)', text)
                if m_sub:
                    subj = m_sub.group(1).strip()
                    # rest as body
                    after = text[m_sub.end():].strip()
                    body = after
                else:
                    # attempt to split first line as subject and rest as body
                    parts = text.split("\n\n", 1)
                    if parts:
                        subj = parts[0].strip()
                        body = parts[1].strip() if len(parts) > 1 else ""

                if subj and body:
                    return {'subject': subj, 'body': body}
                else:
                    print("[GEMINI] Model returned text but parsing failed, falling back to local generator.")
            except Exception as e:
                print(f"[GEMINI] Error using model to generate email content: {e}")

        # MOCK / local generator fallback (still high-quality, avoids echo)
        # Build a natural subject
        if meeting_time and topic:
            subject = f"{topic[:60].capitalize()} — {meeting_time}"
        elif meeting_time:
            subject = f"Meeting at {meeting_time}"
        elif topic:
            short_topic = topic if len(topic) <= 60 else topic[:57] + "..."
            subject = f"Regarding: {short_topic}"
        else:
            subject = f"Quick note from {user_name or ''}".strip()

        # Build a natural body dynamically from the extracted pieces (not static)
        # Greeting
        recip_title = " ".join([p.capitalize() for p in (recipient_name or "").split()][:3]) if recipient_name else ""
        greeting = f"Hi {recip_title}," if recip_title else "Hello,"

        # Compose main paragraph variations to avoid repetitive static text
        paragraphs = []
        if meeting_time and topic:
            paragraphs.append(f"I hope you're well. I'm reaching out to check if you are available at {meeting_time} to discuss {topic}.")
        elif meeting_time:
            paragraphs.append(f"I hope you're well. Are you available for a meeting at {meeting_time}?")
        elif topic:
            paragraphs.append(f"I hope you're well. I'm writing regarding {topic}.")
        else:
            if cleaned:
                paragraphs.append(f"I hope you're well. {cleaned.capitalize()}.")
            else:
                paragraphs.append("I hope you're well. I wanted to get in touch about a quick matter.")

        # second paragraph: CTA tailored to content
        if meeting_time:
            paragraphs.append("Please let me know if that time works for you, or suggest an alternative and I'll adjust accordingly.")
        else:
            paragraphs.append("Would you be able to let me know your availability or thoughts on this?")

        # Combine into body
        lines = [greeting, ""]
        for p in paragraphs:
            lines.append(p)
            lines.append("")

        lines.extend(["Best,", user_name or ""])
        body = "\n".join([ln for ln in lines if ln is not None])

        # Ensure we didn't accidentally include 'send mail' or raw email
        body = re.sub(r'\b(send mail to|send to|send an email to|send email to)\b', '', body, flags=re.I)
        body = re.sub(r'[\w\.-]+@[\w\.-]+\.\w+', '', body)

        return {'subject': subject, 'body': body}

    # -------------------
    # Chat response generator (unchanged)
    # -------------------
    def generate_chat_response(self, message: str, chat_history: List[Dict]) -> str:
        if self.use_mock:
            return f"I understood: \"{message}\" — how can I help with that?"
        try:
            prompt = f"User said: {message}\nChat history: {chat_history}\nReply succinctly."
            resp = self.model.generate_content(prompt)
            return (resp.text or "").strip()
        except Exception as e:
            print(f"[GEMINI] generate_chat_response error: {e}")
            return "Sorry, I couldn't process that due to an internal error."
