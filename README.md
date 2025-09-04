# InboxIQ

InboxIQ is an AI-powered productivity assistant that streamlines email, calendar, and contact management.  
It drafts and saves professional emails, enriches contacts, and keeps track of your communication context — all powered by Gemini 2.5 Flash and backed by Redis memory, Celery, and MySQL persistence.

---

## ✨ Features (V1 Pre-release)
- **Email Drafting:** Generate 1–3 polished drafts per request using Gemini 2.5 Flash.
- **Window Buffer Memory:** Short-term memory with Redis (k=3) to keep conversation context.
- **Gmail Drafts:** Save drafts directly to your Gmail Drafts folder (via Gmail API).
- **Contact Resolution:** Look up emails and names with Google People API.
- **Persistence:** Store user data, conversations, and drafts in MySQL.
- **Background Tasks:** Celery + Redis for queued jobs (token refresh, draft saves).

---

## 🚀 Tech Stack
- **Backend Framework:** Django (REST API)
- **LLM:** Gemini 2.5 Flash
- **Memory:** Redis (conversation buffer)
- **Database:** MySQL
- **Queueing:** Celery with Redis broker
- **Google Integrations:** Gmail API, People API

---

## 📦 Installation

### 1. Clone repo
```bash
git clone https://github.com/<org>/inboxiq.git
cd inboxiq
```

### 2. Setup environment
```bash
cp .env.example .env
# Fill with your own keys/secrets
```

### 3. Start services
```bash
docker-compose up --build
```

### 4. Run migrations & create superuser
```bash
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### 5. Start Celery (if not auto-started)
```bash
docker-compose exec web celery -A inboxiq worker --loglevel=info
```

---

## 🔑 Example `.env.example`
```env
# Django
DJANGO_SECRET_KEY=replace_me
DJANGO_DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# DB (MySQL)
DB_HOST=mysql
DB_PORT=3306
DB_NAME=inboxiq
DB_USER=inboxiq
DB_PASSWORD=changeme

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_URL=redis://redis:6379/0

# Celery
CELERY_BROKER_URL=redis://redis:6379/1
CELERY_RESULT_BACKEND=redis://redis:6379/2

# LLM
GEMINI_API_KEY=your_gemini_server_key_here

# Google OAuth
GOOGLE_CLIENT_ID=your_google_client_id
GOOGLE_CLIENT_SECRET=your_google_client_secret
GOOGLE_OAUTH_REDIRECT=http://localhost:8000/oauth2/callback

# Misc
ENCRYPTION_KEY=32_byte_base64_key
LOG_LEVEL=INFO
```

---

## ⚡ API Quickstart

### Compose Draft
`POST /api/agent/compose`
```json
{
  "user_id": 1,
  "prompt": "Please draft a follow-up email to Priya about the Q3 report.",
  "tone": "concise"
}
```

### Save Draft
`POST /api/gmail/save-draft`
```json
{
  "user_id": 1,
  "draft": {
    "to": "priya@company.com",
    "subject": "Follow-up: Q3 report",
    "body_html": "<p>Hi Priya, just checking in...</p>"
  }
}
```

---

## 🧪 Testing
```bash
docker-compose exec web pytest
```

---

## 📌 Roadmap
- V2: Add safe-send, Calendar propose/create.
- V3: Add web connector (Tavily) for knowledge-backed drafting.
- V4: Business-level insights, CRM sync, analytics dashboards.

---

## 🛡️ Security
- LLM & API keys stay server-side (never exposed to client).
- OAuth2 with Gmail/People API requires user consent.
- Do not deploy without HTTPS, vault-based secrets, and RBAC.

---

## 🤝 Contributing
1. Fork repo & create feature branch (`feat/<feature>`).
2. Run tests before PR (`pytest`).
3. Update docs/sample prompts if adding new features.

---

## 📄 License
MIT License (to be confirmed by project owner)
