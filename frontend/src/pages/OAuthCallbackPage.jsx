import React, { useEffect, useState } from 'react'
import Container from '@mui/material/Container'
import Paper from '@mui/material/Paper'
import Typography from '@mui/material/Typography'
import CircularProgress from '@mui/material/CircularProgress'
import Alert from '@mui/material/Alert'
import Box from '@mui/material/Box'
import { useNavigate, useSearchParams } from 'react-router-dom'

export default function OAuthCallbackPage() {
  const [status, setStatus] = useState('processing')
  const [message, setMessage] = useState('Processing OAuth callback...')
  const navigate = useNavigate()
  const [searchParams] = useSearchParams()

  useEffect(() => {
    const handleCallback = async () => {
      try {
        // Check for URL parameters that indicate OAuth status
        const error = searchParams.get('error')
        const oauthSuccess = searchParams.get('oauth_success')
        
        if (error) {
          throw new Error(`OAuth error: ${error}`)
        }

        if (oauthSuccess === 'true') {
          // OAuth was successful, verify by getting user profile
          const profileResponse = await fetch('/auth/oauth/profile/', {
            credentials: 'include',
            headers: {
              'Accept': 'application/json',
            }
          })

          if (profileResponse.ok) {
            const userData = await profileResponse.json()
            setStatus('success')
            setMessage(`Welcome, ${userData.first_name || userData.username}!`)
            
            setTimeout(() => {
              navigate('/')
            }, 2000)
          } else {
            throw new Error('Failed to get user profile after OAuth')
          }
        } else {
          // If we're here without oauth_success=true, something went wrong
          throw new Error('OAuth callback completed but no success indicator found')
        }
      } catch (err) {
        console.error('OAuth callback error:', err)
        setStatus('error')
        setMessage(err.message)
        
        setTimeout(() => {
          navigate('/login?error=oauth_callback_failed')
        }, 3000)
      }
    }

    handleCallback()
  }, [navigate, searchParams])

  return (
    <Container maxWidth="sm" sx={{ py: 8 }}>
      <Paper elevation={2} sx={{ p: 4, textAlign: 'center' }}>
        <Typography variant="h5" sx={{ mb: 3 }}>
          OAuth Authentication
        </Typography>

        <Box sx={{ mb: 3 }}>
          {status === 'processing' && (
            <>
              <CircularProgress sx={{ mb: 2 }} />
              <Typography color="text.secondary">
                {message}
              </Typography>
            </>
          )}

          {status === 'success' && (
            <Alert severity="success" sx={{ mb: 2 }}>
              {message}
            </Alert>
          )}

          {status === 'error' && (
            <Alert severity="error" sx={{ mb: 2 }}>
              {message}
            </Alert>
          )}
        </Box>

        {status === 'success' && (
          <Typography variant="body2" color="text.secondary">
            Redirecting to dashboard...
          </Typography>
        )}

        {status === 'error' && (
          <Typography variant="body2" color="text.secondary">
            Redirecting to login page...
          </Typography>
        )}
      </Paper>
    </Container>
  )
}