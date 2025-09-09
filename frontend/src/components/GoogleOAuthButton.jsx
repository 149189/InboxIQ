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
      // Use relative path - will be proxied to backend by Vite
      const response = await fetch('/auth/oauth/google/login/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Accept': 'application/json',
          'Content-Type': 'application/json',
        }
      })
      
      if (!response.ok) {
        const errorText = await response.text()
        throw new Error(`Failed to initiate OAuth login: ${response.status} ${errorText}`)
      }
      
      const data = await response.json()
      
      if (data.auth_url) {
        console.log('Redirecting to:', data.auth_url)
        // Redirect to Google OAuth
        window.location.href = data.auth_url
      } else {
        throw new Error('No auth URL received from server')
      }
    } catch (err) {
      console.error('OAuth login error:', err)
      setError(err.message || 'Failed to connect to authentication service')
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