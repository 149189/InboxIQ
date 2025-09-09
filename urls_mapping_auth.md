# Complete URL Mapping Reference

## Backend URLs (Django - Port 8000)
```
http://127.0.0.1:8000/admin/                     → Django admin
http://127.0.0.1:8000/auth/register/             → User registration
http://127.0.0.1:8000/auth/login/                → User login
http://127.0.0.1:8000/auth/logout/               → User logout
http://127.0.0.1:8000/oauth/google/login/        → Initiate OAuth
http://127.0.0.1:8000/oauth/google/callback/     → Google redirects here
http://127.0.0.1:8000/oauth/google/refresh/      → Refresh tokens
http://127.0.0.1:8000/oauth/profile/             → Get user profile
```

## Frontend URLs (React - Port 5173)
```
http://localhost:5173/                           → Home page
http://localhost:5173/login                      → Login page
http://localhost:5173/register                   → Register page  
http://localhost:5173/oauth/callback             → OAuth success handler
```

## Frontend API Calls (Proxied to Backend)
```
Frontend URL                 → Proxied to Backend URL
/auth/register/             → http://127.0.0.1:8000/auth/register/
/auth/login/                → http://127.0.0.1:8000/auth/login/
/auth/logout/               → http://127.0.0.1:8000/auth/logout/
/oauth/google/login/        → http://127.0.0.1:8000/oauth/google/login/
/oauth/profile/             → http://127.0.0.1:8000/oauth/profile/
/oauth/google/refresh/      → http://127.0.0.1:8000/oauth/google/refresh/
```

## OAuth Flow URL Sequence
1. **User clicks OAuth button**
   - Frontend: `GET /oauth/google/login/`
   - Proxied to: `http://127.0.0.1:8000/oauth/google/login/`

2. **Backend returns Google OAuth URL**
   - Example: `https://accounts.google.com/o/oauth2/auth?client_id=...`

3. **Browser redirects to Google**
   - User authenticates with Google

4. **Google redirects back**
   - Target: `http://127.0.0.1:8000/oauth/google/callback/?code=...&state=...`

5. **Backend processes callback**
   - Creates/updates user
   - Logs user in
   - Redirects to: `http://localhost:5173/login?oauth_success=true`

6. **Frontend handles success**
   - Shows success message
   - Redirects to dashboard

## Google Cloud Console Configuration
**Authorized JavaScript origins:**
```
http://localhost:5173
http://127.0.0.1:5173
http://localhost:8000
http://127.0.0.1:8000
```

**Authorized redirect URIs:**
```
http://127.0.0.1:8000/oauth/google/callback/
```

## Environment Variables
```env
# Backend (.env)
GOOGLE_OAUTH_CLIENT_ID=your_client_id
GOOGLE_OAUTH_CLIENT_SECRET=your_client_secret
GOOGLE_OAUTH_REDIRECT_URI=http://127.0.0.1:8000/auth/oauth/google/callback/
FRONTEND_URL=http://localhost:5173
```

## Key Points
- ✅ Use `127.0.0.1` for backend in OAuth redirect URI
- ✅ Use `localhost` for frontend in FRONTEND_URL
- ✅ Frontend uses relative URLs (proxied by Vite)
- ✅ All URLs include trailing slashes where expected
- ✅ CORS allows both localhost and 127.0.0.1