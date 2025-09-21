// src/components/Footer.jsx
import React from 'react'
import { Box, Container, Typography, Link, Divider } from '@mui/material'

export default function Footer() {
  return (
    <Box 
      component="footer" 
      sx={{ 
        backgroundColor: '#f8f9fa',
        borderTop: '1px solid #e0e0e0',
        mt: 'auto'
      }}
    >
      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', md: 'row' },
            justifyContent: 'space-between',
            alignItems: { xs: 'center', md: 'flex-start' },
            gap: 3
          }}
        >
          {/* Logo and Description */}
          <Box sx={{ textAlign: { xs: 'center', md: 'left' } }}>
            <Typography
              variant="h6"
              sx={{
                fontFamily: 'Google Sans, Roboto, sans-serif',
                fontWeight: 500,
                color: '#202124',
                mb: 1
              }}
            >
              <Box
                component="span"
                sx={{
                  background: 'linear-gradient(45deg, #4285f4, #34a853, #fbbc04, #ea4335)',
                  backgroundClip: 'text',
                  WebkitBackgroundClip: 'text',
                  WebkitTextFillColor: 'transparent',
                  fontWeight: 500,
                  mr: 0.5
                }}
              >
                Inbox
              </Box>
              <Box component="span" sx={{ color: '#5f6368' }}>
                IQ
              </Box>
            </Typography>
            <Typography
              variant="body2"
              sx={{
                color: '#5f6368',
                maxWidth: '300px'
              }}
            >
              Your AI-powered productivity assistant for smarter email management
            </Typography>
          </Box>

          {/* Links */}
          <Box
            sx={{
              display: 'flex',
              flexDirection: { xs: 'column', sm: 'row' },
              gap: { xs: 2, sm: 4 },
              textAlign: { xs: 'center', md: 'left' }
            }}
          >
            <Box>
              <Typography
                variant="subtitle2"
                sx={{
                  color: '#202124',
                  fontWeight: 500,
                  mb: 1,
                  fontSize: '0.875rem'
                }}
              >
                Product
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                <Link
                  href="/chat"
                  sx={{
                    color: '#5f6368',
                    textDecoration: 'none',
                    fontSize: '0.8rem',
                    '&:hover': {
                      color: '#1a73e8',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  Chat Assistant
                </Link>
                <Link
                  href="#"
                  sx={{
                    color: '#5f6368',
                    textDecoration: 'none',
                    fontSize: '0.8rem',
                    '&:hover': {
                      color: '#1a73e8',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  Email Drafts
                </Link>
                <Link
                  href="#"
                  sx={{
                    color: '#5f6368',
                    textDecoration: 'none',
                    fontSize: '0.8rem',
                    '&:hover': {
                      color: '#1a73e8',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  Contact Management
                </Link>
              </Box>
            </Box>

            <Box>
              <Typography
                variant="subtitle2"
                sx={{
                  color: '#202124',
                  fontWeight: 500,
                  mb: 1,
                  fontSize: '0.875rem'
                }}
              >
                Support
              </Typography>
              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 0.5 }}>
                <Link
                  href="#"
                  sx={{
                    color: '#5f6368',
                    textDecoration: 'none',
                    fontSize: '0.8rem',
                    '&:hover': {
                      color: '#1a73e8',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  Help Center
                </Link>
                <Link
                  href="#"
                  sx={{
                    color: '#5f6368',
                    textDecoration: 'none',
                    fontSize: '0.8rem',
                    '&:hover': {
                      color: '#1a73e8',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  Privacy Policy
                </Link>
                <Link
                  href="#"
                  sx={{
                    color: '#5f6368',
                    textDecoration: 'none',
                    fontSize: '0.8rem',
                    '&:hover': {
                      color: '#1a73e8',
                      textDecoration: 'underline'
                    }
                  }}
                >
                  Terms of Service
                </Link>
              </Box>
            </Box>
          </Box>
        </Box>

        <Divider sx={{ my: 3, borderColor: '#e0e0e0' }} />

        <Box
          sx={{
            display: 'flex',
            flexDirection: { xs: 'column', sm: 'row' },
            justifyContent: 'space-between',
            alignItems: 'center',
            gap: 2
          }}
        >
          <Typography
            variant="body2"
            sx={{
              color: '#5f6368',
              fontSize: '0.8rem'
            }}
          >
            © {new Date().getFullYear()} InboxIQ. All rights reserved.
          </Typography>
          
          <Typography
            variant="body2"
            sx={{
              color: '#5f6368',
              fontSize: '0.8rem',
              display: 'flex',
              alignItems: 'center',
              gap: 0.5
            }}
          >
            Powered by
            <Box
              component="span"
              sx={{
                color: '#4285f4',
                fontWeight: 500
              }}
            >
              Gemini 2.5 Flash
            </Box>
          </Typography>
        </Box>
      </Container>
    </Box>
  )
}
