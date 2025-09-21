// src/pages/RegisterPage.jsx
import React, { useState } from 'react'
import {
  Container,
  Paper,
  Typography,
  TextField,
  Button,
  Alert,
  Stack,
  Divider,
  Box,
  Link
} from '@mui/material'
import { Link as RouterLink, useNavigate } from 'react-router-dom'
import GoogleOAuthButton from '../components/GoogleOAuthButton'

export default function RegisterPage() {
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState(null)
  const [success, setSuccess] = useState(null)
  const navigate = useNavigate()

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)
    
    try {
      // Use relative URL - will be proxied to backend
      const res = await fetch('/auth/register/', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Accept': 'application/json'
        },
        credentials: 'include',
        body: JSON.stringify({ username, password }),
      })
      
      const data = await res.json()
      if (!res.ok) throw new Error(data.error || 'Registration failed')
      
      setSuccess('Account created successfully! Redirecting to login...')
      setTimeout(() => {
        navigate('/login')
      }, 2000)
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <Box sx={{ 
      minHeight: 'calc(100vh - 64px)', 
      backgroundColor: '#f8f9fa',
      display: 'flex',
      alignItems: 'center',
      py: 4
    }}>
      <Container maxWidth="sm">
        <Box sx={{ textAlign: 'center', mb: 4 }}>
          <Typography
            variant="h4"
            component="h1"
            sx={{
              fontWeight: 400,
              color: '#202124',
              mb: 1,
              fontFamily: 'Google Sans, Roboto, sans-serif'
            }}
          >
            Create your{' '}
            <Box
              component="span"
              sx={{
                background: 'linear-gradient(45deg, #4285f4, #34a853, #fbbc04, #ea4335)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontWeight: 500
              }}
            >
              InboxIQ
            </Box>
            {' '}account
          </Typography>
          <Typography
            variant="body1"
            sx={{
              color: '#5f6368',
              fontWeight: 400
            }}
          >
            Start managing your emails smarter with AI assistance
          </Typography>
        </Box>

        <Paper 
          elevation={0}
          sx={{ 
            p: { xs: 4, sm: 6 },
            border: '1px solid #dadce0',
            borderRadius: '8px',
            backgroundColor: '#ffffff'
          }}
        >
          <Stack spacing={3}>
            {error && (
              <Alert 
                severity="error"
                sx={{
                  borderRadius: '8px',
                  '& .MuiAlert-message': {
                    color: '#d93025'
                  }
                }}
              >
                {error}
              </Alert>
            )}
            {success && (
              <Alert 
                severity="success"
                sx={{
                  borderRadius: '8px',
                  '& .MuiAlert-message': {
                    color: '#137333'
                  }
                }}
              >
                {success}
              </Alert>
            )}

            {/* Google OAuth Button */}
            <GoogleOAuthButton 
              onError={(errorMsg) => setError(errorMsg)}
            />

            <Box sx={{ display: 'flex', alignItems: 'center', my: 3 }}>
              <Divider sx={{ flexGrow: 1, borderColor: '#dadce0' }} />
              <Typography 
                variant="body2" 
                sx={{ 
                  mx: 3, 
                  color: '#5f6368',
                  fontSize: '0.875rem'
                }}
              >
                or create account with username
              </Typography>
              <Divider sx={{ flexGrow: 1, borderColor: '#dadce0' }} />
            </Box>

            {/* Traditional Registration Form */}
            <Stack component="form" spacing={3} onSubmit={handleSubmit}>
              <TextField
                label="Username"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                fullWidth
                required
                variant="outlined"
                helperText="Choose a unique username"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px',
                    '& fieldset': {
                      borderColor: '#dadce0',
                    },
                    '&:hover fieldset': {
                      borderColor: '#5f6368',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1a73e8',
                      borderWidth: '2px',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: '#5f6368',
                    '&.Mui-focused': {
                      color: '#1a73e8',
                    },
                  },
                  '& .MuiFormHelperText-root': {
                    color: '#5f6368',
                    fontSize: '0.75rem',
                  },
                }}
              />
              <TextField
                label="Password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                fullWidth
                required
                variant="outlined"
                helperText="Use a strong password with at least 8 characters"
                sx={{
                  '& .MuiOutlinedInput-root': {
                    borderRadius: '8px',
                    '& fieldset': {
                      borderColor: '#dadce0',
                    },
                    '&:hover fieldset': {
                      borderColor: '#5f6368',
                    },
                    '&.Mui-focused fieldset': {
                      borderColor: '#1a73e8',
                      borderWidth: '2px',
                    },
                  },
                  '& .MuiInputLabel-root': {
                    color: '#5f6368',
                    '&.Mui-focused': {
                      color: '#1a73e8',
                    },
                  },
                  '& .MuiFormHelperText-root': {
                    color: '#5f6368',
                    fontSize: '0.75rem',
                  },
                }}
              />

              <Button 
                type="submit" 
                variant="contained"
                size="large"
                sx={{
                  py: 1.5,
                  fontSize: '1rem',
                  fontWeight: 500,
                  borderRadius: '24px',
                  textTransform: 'none',
                  backgroundColor: '#34a853',
                  boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
                  '&:hover': {
                    backgroundColor: '#137333',
                    boxShadow: '0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)',
                  }
                }}
              >
                Create Account
              </Button>
            </Stack>

            <Box sx={{ textAlign: 'center', mt: 4 }}>
              <Typography variant="body2" sx={{ color: '#5f6368' }}>
                Already have an account?{' '}
                <Link
                  component={RouterLink}
                  to="/login"
                  sx={{
                    color: '#1a73e8',
                    textDecoration: 'none',
                    fontWeight: 500,
                    '&:hover': {
                      textDecoration: 'underline'
                    }
                  }}
                >
                  Sign in
                </Link>
              </Typography>
            </Box>
          </Stack>
        </Paper>

        <Box sx={{ textAlign: 'center', mt: 4 }}>
          <Typography variant="caption" sx={{ color: '#5f6368' }}>
            By creating an account, you agree to our Terms of Service and Privacy Policy
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}