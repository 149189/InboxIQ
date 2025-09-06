import React, { useState } from 'react'
import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress'
import GoogleIcon from '@mui/icons-material/Google'
import Alert from '@mui/material/Alert'

export default function GoogleOAuthButton({ onError }) {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleGoogleLogin = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Use relative path with proxy (if configured in vite.config.js)
      const response = await fetch('/oauth/google/login/', {
        method: 'GET',
        credentials: 'include',
      })
      
      if (!response.ok) {
        throw new Error('Failed to initiate OAuth login')
      }
      
      const data = await response.json()
      
      if (data.auth_url) {
        // Add a fallback in case the redirect doesn't work
        window.location.href = data.auth_url;
        
        // Set a timeout to handle cases where the redirect might fail
        setTimeout(() => {
          setLoading(false);
          setError('Redirect to Google authentication failed. Please check your browser settings and try again.');
        }, 3000);
      } else {
        throw new Error('No auth URL received from server');
      }
    } catch (err) {
      setError(err.message || 'Failed to connect to authentication service. Please check your browser extensions and try again.');
      setLoading(false)
      if (onError) onError(err.message)
    }
  }

  return (
    <>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}
      <Button
        variant="outlined"
        fullWidth
        onClick={handleGoogleLogin}
        disabled={loading}
        startIcon={loading ? <CircularProgress size={20} /> : <GoogleIcon />}
        sx={{
          borderColor: '#4285f4',
          color: '#4285f4',
          '&:hover': {
            borderColor: '#3367d6',
            backgroundColor: 'rgba(66, 133, 244, 0.04)',
          },
        }}
      >
        {loading ? 'Connecting...' : 'Continue with Google'}
      </Button>
    </>
  )
}