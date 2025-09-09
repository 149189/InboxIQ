# Google OAuth Implementation Guide

## Overview
This Django application now includes Google OAuth authentication alongside traditional username/password authentication. Users can sign in with their Google accounts and the system will automatically create user accounts and manage OAuth tokens.

## Setup Instructions

### 1. Google Cloud Console Setup
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the Google+ API and Gmail API
4. Go to "Credentials" → "Create Credentials" → "OAuth 2.0 Client IDs"
5. Configure the OAuth consent screen
6. Set up OAuth 2.0 Client ID:
   - Application type: Web application
   - Authorized redirect URIs: `http://localhost:8000/oauth/google/callback/`

### 2. Environment Configuration
Update the `.env` file with your Google OAuth credentials:

```env
GOOGLE_OAUTH_CLIENT_ID=your_actual_google_client_id_here
GOOGLE_OAUTH_CLIENT_SECRET=your_actual_google_client_secret_here
```

### 3. Database Migration
The migration has already been applied, but if you need to run it again:
```bash
python manage.py migrate
```

## API Endpoints

### OAuth Endpoints
- `GET /oauth/google/login/` - Initiate Google OAuth login
- `GET /oauth/google/callback/` - Handle OAuth callback (used by Google)
- `POST /oauth/google/refresh/` - Refresh expired access token
- `GET /oauth/profile/` - Get current user profile

### Traditional Auth Endpoints (still available)
- `POST /auth/register/` - Register with username/password
- `POST /auth/login/` - Login with username/password
- `POST /auth/logout/` - Logout

## OAuth Flow

### 1. Initiate OAuth Login
```javascript
// Frontend JavaScript example
fetch('/oauth/google/login/')
  .then(response => response.json())
  .then(data => {
    // Redirect user to Google OAuth
    window.location.href = data.auth_url;
  });
```

### 2. Handle OAuth Callback
Google will redirect to `/oauth/google/callback/` automatically. The backend will:
- Verify the state parameter
- Exchange authorization code for tokens
- Get user info from Google
- Create or update user account
- Log in the user
- Redirect to frontend dashboard

### 3. Access User Profile
```javascript
// Get current user profile
fetch('/oauth/profile/')
  .then(response => response.json())
  .then(user => {
    console.log('User:', user);
    // user object contains: id, username, email, first_name, last_name, etc.
  });
```

### 4. Refresh Token (if needed)
```javascript
// Refresh expired access token
fetch('/oauth/google/refresh/', {
  method: 'POST',
  headers: {
    'X-CSRFToken': getCsrfToken(), // Get CSRF token
  }
})
.then(response => response.json())
.then(data => {
  console.log('Token refreshed:', data);
});
```

## User Model Fields

The `CustomUser` model now includes OAuth-specific fields:
- `google_id` - Google user ID
- `email` - User's email from Google
- `first_name` - First name from Google
- `last_name` - Last name from Google
- `access_token` - OAuth access token (encrypted storage recommended)
- `refresh_token` - OAuth refresh token (encrypted storage recommended)
- `token_expires_at` - Token expiration timestamp
- `profile_picture` - URL to user's Google profile picture

## Security Considerations

1. **Environment Variables**: Never commit actual OAuth credentials to version control
2. **HTTPS**: Use HTTPS in production for OAuth callbacks
3. **Token Storage**: Consider encrypting stored tokens in production
4. **State Parameter**: The implementation uses a secure random state parameter to prevent CSRF attacks
5. **Token Refresh**: Implement automatic token refresh for long-running sessions

## Testing the Implementation

### 1. Start the Django Server
```bash
cd backend/inboxiq_project
python manage.py runserver
```

### 2. Test OAuth Login Flow
1. Visit: `http://localhost:8000/oauth/google/login/`
2. You should get a JSON response with `auth_url`
3. Visit the `auth_url` in your browser
4. Complete Google OAuth flow
5. You should be redirected back to your frontend

### 3. Test API Endpoints
```bash
# Test OAuth login initiation
curl http://localhost:8000/oauth/google/login/

# Test user profile (requires authentication)
curl -b cookies.txt http://localhost:8000/oauth/profile/
```

## Frontend Integration

### React Example
```jsx
const GoogleOAuthButton = () => {
  const handleGoogleLogin = async () => {
    try {
      const response = await fetch('/oauth/google/login/');
      const data = await response.json();
      window.location.href = data.auth_url;
    } catch (error) {
      console.error('OAuth login failed:', error);
    }
  };

  return (
    <button onClick={handleGoogleLogin}>
      Sign in with Google
    </button>
  );
};
```

## Troubleshooting

### Common Issues
1. **Invalid redirect URI**: Ensure the redirect URI in Google Console matches exactly
2. **Missing scopes**: Check that required scopes are configured in settings
3. **Token expired**: Implement token refresh logic
4. **CORS issues**: Ensure CORS is properly configured for your frontend domain

### Debug Mode
Set `DEBUG = True` in Django settings to see detailed error messages during development.

## Gmail API Integration

The OAuth implementation includes Gmail API scopes:
- `https://www.googleapis.com/auth/gmail.readonly` - Read Gmail messages
- `https://www.googleapis.com/auth/gmail.modify` - Modify Gmail messages

You can use the stored `access_token` to make Gmail API calls:

```python
import requests

def get_gmail_messages(user):
    if user.is_token_expired():
        # Refresh token first
        pass
    
    headers = {'Authorization': f'Bearer {user.access_token}'}
    response = requests.get(
        'https://www.googleapis.com/gmail/v1/users/me/messages',
        headers=headers
    )
    return response.json()
```

## Production Deployment

1. Set `DEBUG = False`
2. Use environment variables for all secrets
3. Configure proper ALLOWED_HOSTS
4. Use HTTPS for OAuth callbacks
5. Consider using encrypted database fields for tokens
6. Set up proper logging for OAuth events
