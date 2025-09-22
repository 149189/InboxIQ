# 🚀 InboxIQ Deployment Guide

This guide will help you deploy InboxIQ to production with a React frontend and Django backend.

## 📋 Prerequisites

1. **GitHub Repository** - Push your code to GitHub
2. **Google Cloud Console** - Set up OAuth credentials for production
3. **Database** - PostgreSQL database (recommended)

## 🎯 Recommended Architecture

**Frontend:** Netlify (React/Vite)  
**Backend:** Railway or Render (Django)  
**Database:** PostgreSQL (Railway/Render included)

---

## 🔧 Backend Deployment (Railway - Recommended)

### Step 1: Prepare Environment Variables

Create these environment variables in Railway:

```env
# Django Settings
DJANGO_SETTINGS_MODULE=inboxiq_project.settings_production
SECRET_KEY=your-super-secret-key-here
DEBUG=False

# Database (Railway provides automatically)
DB_NAME=railway
DB_USER=postgres
DB_PASSWORD=auto-generated
DB_HOST=auto-generated
DB_PORT=5432

# Google OAuth (from Google Cloud Console)
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_OAUTH_REDIRECT_URI=https://your-backend.railway.app/auth/oauth/google/callback/

# Gemini AI (optional)
GEMINI_API_KEY=your-gemini-api-key

# Frontend URL
FRONTEND_URL=https://your-app.netlify.app
ALLOWED_HOST=your-backend.railway.app
```

### Step 2: Deploy to Railway

1. **Connect Repository:**
   ```bash
   # Install Railway CLI
   npm install -g @railway/cli
   
   # Login and deploy
   railway login
   railway link
   railway up
   ```

2. **Or use Railway Dashboard:**
   - Go to [railway.app](https://railway.app)
   - Connect your GitHub repository
   - Select the `backend` folder as root
   - Add environment variables
   - Deploy!

### Step 3: Database Setup

Railway automatically provisions PostgreSQL. Update your production settings:

```python
# In settings_production.py - already configured!
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME'),
        'USER': config('DB_USER'),
        'PASSWORD': config('DB_PASSWORD'),
        'HOST': config('DB_HOST'),
        'PORT': config('DB_PORT'),
    }
}
```

---

## 🎨 Frontend Deployment (Netlify)

### Step 1: Update API URLs

Update your frontend to use production backend URL:

```javascript
// Create .env.production in frontend folder
VITE_API_BASE_URL=https://your-backend.railway.app
```

### Step 2: Deploy to Netlify

1. **Automatic Deployment:**
   - Go to [netlify.com](https://netlify.com)
   - Connect your GitHub repository
   - Set build settings:
     - **Base directory:** `frontend`
     - **Build command:** `npm run build`
     - **Publish directory:** `frontend/dist`

2. **Manual Deployment:**
   ```bash
   # Build the frontend
   cd frontend
   npm run build
   
   # Deploy to Netlify
   npm install -g netlify-cli
   netlify deploy --prod --dir=dist
   ```

### Step 3: Configure Environment Variables

In Netlify dashboard, add:
```env
VITE_API_BASE_URL=https://your-backend.railway.app
```

---

## 🔐 Google OAuth Setup

### Step 1: Update OAuth Settings

In Google Cloud Console:

1. **Authorized JavaScript origins:**
   ```
   https://your-app.netlify.app
   ```

2. **Authorized redirect URIs:**
   ```
   https://your-backend.railway.app/auth/oauth/google/callback/
   ```

### Step 2: Update Backend Settings

Update your production environment variables:
```env
GOOGLE_OAUTH_REDIRECT_URI=https://your-backend.railway.app/auth/oauth/google/callback/
```

---

## 🗄️ Database Migration

After deployment, run migrations:

```bash
# Railway automatically runs migrations via Procfile
# But you can also run manually:
railway run python manage.py migrate
railway run python manage.py collectstatic --noinput
```

---

## 🔧 Alternative Hosting Options

### Option 2: Render

**Backend on Render:**
1. Connect GitHub repository
2. Select `backend` folder
3. Use these settings:
   - **Build Command:** `cd inboxiq_project && pip install -r ../requirements.txt`
   - **Start Command:** `cd inboxiq_project && gunicorn inboxiq_project.wsgi:application`

### Option 3: Heroku

**Backend on Heroku:**
```bash
# Install Heroku CLI
heroku create your-app-name
heroku addons:create heroku-postgresql:hobby-dev
heroku config:set DJANGO_SETTINGS_MODULE=inboxiq_project.settings_production
git push heroku main
```

### Option 4: Vercel (Frontend Alternative)

**Frontend on Vercel:**
```bash
npm install -g vercel
cd frontend
vercel --prod
```

---

## 📊 Monitoring & Maintenance

### Health Checks

Add health check endpoints:
```python
# In Django urls.py
path('health/', lambda request: JsonResponse({'status': 'healthy'})),
```

### Logging

Monitor your application:
- **Railway:** Built-in logging dashboard
- **Netlify:** Function logs and analytics
- **Sentry:** Error tracking (recommended)

---

## 🚀 Quick Deploy Commands

### One-Click Railway Deploy

```bash
# Clone and deploy backend
git clone your-repo
cd InboxIQ/backend
railway login
railway up
```

### One-Click Netlify Deploy

```bash
# Deploy frontend
cd InboxIQ/frontend
npm install
npm run build
netlify deploy --prod --dir=dist
```

---

## 🔍 Troubleshooting

### Common Issues:

1. **CORS Errors:** Update `CORS_ALLOWED_ORIGINS` in production settings
2. **OAuth Redirect:** Ensure redirect URIs match exactly
3. **Static Files:** Run `collectstatic` command
4. **Database:** Check connection strings and migrations

### Debug Commands:

```bash
# Railway debugging
railway logs
railway shell

# Check Django settings
python manage.py check --deploy
```

---

## 🎉 Success!

Your InboxIQ application should now be live at:
- **Frontend:** `https://your-app.netlify.app`
- **Backend:** `https://your-backend.railway.app`

Test all functionality:
- ✅ Gmail OAuth login
- ✅ Email composition and sending
- ✅ Calendar integration
- ✅ Chat functionality

---

## 📞 Need Help?

If you encounter issues:
1. Check the logs in Railway/Netlify dashboards
2. Verify environment variables are set correctly
3. Test OAuth redirect URIs
4. Ensure database migrations completed

Happy deploying! 🚀
