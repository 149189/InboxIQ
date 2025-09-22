# 🚀 GitHub Actions Workflows for InboxIQ

This directory contains automated CI/CD workflows for the InboxIQ application.

## 📋 Workflows Overview

### 1. **ci.yml** - Continuous Integration
**Triggers:** Push/PR to main, master, develop branches
- ✅ **Linting & Formatting** - ESLint, Prettier, Flake8, Black, isort
- 🔒 **Security Scanning** - npm audit, safety, bandit
- 🧪 **Matrix Testing** - Multiple Node.js and Python versions
- 📦 **Dependency Review** - Automated dependency vulnerability checks
- 🏗️ **Build & Test** - Full application build and test suite

### 2. **deploy-frontend.yml** - Frontend Deployment
**Triggers:** Push to main/master with frontend changes
- 🎨 **Frontend-only deployment** to Netlify
- 🧪 **Testing** before deployment
- 💬 **PR Comments** with deployment URLs

### 3. **deploy-backend.yml** - Backend Deployment
**Triggers:** Push to main/master with backend changes
- 🔧 **Backend-only deployment** to Railway
- 🗄️ **Database testing** with PostgreSQL
- 🏥 **Health checks** after deployment

### 4. **full-stack-deploy.yml** - Complete Deployment
**Triggers:** Push to main/master, manual dispatch
- 🔄 **Smart change detection** - Only deploys what changed
- 🎯 **Parallel deployment** of frontend and backend
- 🧪 **Integration testing** after deployment
- 📊 **Deployment summary** and notifications

## 🔧 Required Secrets

Add these secrets in your GitHub repository settings:

### Netlify Secrets
```
NETLIFY_AUTH_TOKEN=your-netlify-auth-token
NETLIFY_SITE_ID=your-netlify-site-id
```

### Railway Secrets
```
RAILWAY_TOKEN=your-railway-token
RAILWAY_SERVICE_ID=your-railway-service-id
```

### Application URLs
```
FRONTEND_URL=https://your-app.netlify.app
BACKEND_URL=https://your-backend.railway.app
VITE_API_BASE_URL=https://your-backend.railway.app
```

## 🚀 Setup Instructions

### Step 1: Get Netlify Tokens
1. Go to [Netlify](https://netlify.com) → User Settings → Applications
2. Create a new personal access token
3. Deploy your site once manually to get the Site ID

### Step 2: Get Railway Tokens
1. Go to [Railway](https://railway.app) → Account Settings → Tokens
2. Create a new token
3. Deploy your service once to get the Service ID

### Step 3: Add Secrets to GitHub
1. Go to your GitHub repository
2. Settings → Secrets and variables → Actions
3. Add all the required secrets listed above

### Step 4: Configure Branch Protection (Optional)
1. Settings → Branches → Add rule
2. Require status checks to pass before merging
3. Select the CI workflow checks

## 📊 Workflow Features

### 🎯 Smart Deployment
- **Path-based triggers** - Only runs when relevant files change
- **Parallel execution** - Frontend and backend deploy simultaneously
- **Artifact caching** - Faster builds with dependency caching

### 🧪 Comprehensive Testing
- **Multi-version testing** - Node.js 16, 18, 20 and Python 3.9, 3.10, 3.11
- **Database integration** - PostgreSQL service for backend tests
- **Security scanning** - Automated vulnerability detection

### 🔒 Security & Quality
- **Dependency review** - Automatic security checks on PRs
- **Code quality** - Linting and formatting enforcement
- **Coverage reporting** - Test coverage tracking with Codecov

### 📱 Notifications
- **PR comments** - Deployment URLs and status updates
- **Status badges** - Workflow status in README
- **Slack/Discord** - Optional team notifications (can be added)

## 🔄 Workflow Triggers

| Workflow | Push | PR | Manual | Schedule |
|----------|------|----|---------|---------| 
| CI | ✅ | ✅ | ❌ | ❌ |
| Frontend Deploy | ✅ | ❌ | ❌ | ❌ |
| Backend Deploy | ✅ | ❌ | ❌ | ❌ |
| Full Stack Deploy | ✅ | ✅ | ✅ | ❌ |

## 🛠️ Customization

### Adding Environment Variables
```yaml
- name: Create environment file
  run: |
    echo "CUSTOM_VAR=${{ secrets.CUSTOM_VAR }}" >> .env
```

### Adding Slack Notifications
```yaml
- name: Slack Notification
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Adding More Tests
```yaml
- name: E2E Tests
  run: npm run test:e2e
```

## 🐛 Troubleshooting

### Common Issues:

1. **Deployment fails** - Check secrets are correctly set
2. **Tests timeout** - Increase timeout in workflow
3. **Build fails** - Check Node.js/Python versions match local
4. **Database connection** - Ensure PostgreSQL service is healthy

### Debug Commands:
```yaml
- name: Debug Environment
  run: |
    echo "Node version: $(node --version)"
    echo "Python version: $(python --version)"
    echo "Working directory: $(pwd)"
    ls -la
```

## 📈 Monitoring

### Workflow Status
- Check the **Actions** tab in your GitHub repository
- Green checkmarks = successful deployments
- Red X = failed deployments (check logs)

### Deployment URLs
- Frontend: Automatically commented on PRs
- Backend: Available in workflow logs
- Health checks: Automated after deployment

## 🎉 Benefits

✅ **Automated Deployment** - Push to deploy  
✅ **Quality Assurance** - Tests run before deployment  
✅ **Security Scanning** - Vulnerability detection  
✅ **Multi-environment** - Production and staging support  
✅ **Fast Feedback** - PR checks and comments  
✅ **Rollback Ready** - Easy to revert deployments  

Happy deploying! 🚀
