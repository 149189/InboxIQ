// src/pages/WelcomePage.jsx
import React from 'react'
import {
  Container,
  Typography,
  Button,
  Box,
  Card,
  CardContent,
  Avatar,
  Chip,
  Grid
} from '@mui/material'
import EmailIcon from '@mui/icons-material/Email'
import MemoryIcon from '@mui/icons-material/Memory'
import SecurityIcon from '@mui/icons-material/Security'
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome'
import SpeedIcon from '@mui/icons-material/Speed'
import IntegrationIcon from '@mui/icons-material/IntegrationInstructions'
import { Link as RouterLink } from 'react-router-dom'


export default function WelcomePage() {
  const features = [
    {
      icon: <EmailIcon sx={{ fontSize: 40, color: '#4285f4' }} />,
      title: 'AI-Powered Email Drafts',
      description: 'Transform rough prompts into professional email drafts using Gemini 2.5 Flash. Get 1-3 polished options instantly.',
      color: '#4285f4'
    },
    {
      icon: <MemoryIcon sx={{ fontSize: 40, color: '#34a853' }} />,
      title: 'Context Memory',
      description: 'Smart conversation buffer remembers your context across sessions for coherent follow-up interactions.',
      color: '#34a853'
    },
    {
      icon: <SecurityIcon sx={{ fontSize: 40, color: '#ea4335' }} />,
      title: 'Safe Gmail Integration',
      description: 'Securely save drafts to Gmail with OAuth2. No unexpected sends - everything requires your confirmation.',
      color: '#ea4335'
    },
    {
      icon: <AutoAwesomeIcon sx={{ fontSize: 40, color: '#fbbc04' }} />,
      title: 'Smart Contact Resolution',
      description: 'Automatically find and suggest contacts using Google People API for seamless email addressing.',
      color: '#fbbc04'
    },
    {
      icon: <SpeedIcon sx={{ fontSize: 40, color: '#4285f4' }} />,
      title: 'Lightning Fast',
      description: 'Powered by Redis memory and Celery background tasks for instant responses and smooth performance.',
      color: '#4285f4'
    },
    {
      icon: <IntegrationIcon sx={{ fontSize: 40, color: '#34a853' }} />,
      title: 'Google Workspace Ready',
      description: 'Built for Google Workspace users with Gmail API, Google People API, and OAuth2 integration.',
      color: '#34a853'
    }
  ]

  return (
    <Box sx={{ backgroundColor: '#f8f9fa', minHeight: 'calc(100vh - 64px)' }}>
      {/* Hero Section */}
      <Container maxWidth="lg">
        <Box sx={{ pt: { xs: 6, md: 10 }, pb: { xs: 6, md: 8 }, textAlign: 'center' }}>
          <Typography
            variant="h2"
            component="h1"
            sx={{
              fontWeight: 400,
              color: '#202124',
              mb: 3,
              fontSize: { xs: '2.5rem', md: '3.5rem' },
              fontFamily: 'Google Sans, Roboto, sans-serif'
            }}
          >
            Meet{' '}
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
          </Typography>

          <Typography
            variant="h5"
            sx={{
              color: '#5f6368',
              mb: 4,
              maxWidth: '800px',
              mx: 'auto',
              fontWeight: 400,
              lineHeight: 1.4
            }}
          >
            Your AI-powered productivity assistant that transforms email management with intelligent drafting, 
            context memory, and seamless Gmail integration.
          </Typography>

          <Box sx={{ display: 'flex', gap: 2, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Button
              component={RouterLink}
              to="/chat"
              variant="contained"
              size="large"
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 500,
                borderRadius: '24px',
                textTransform: 'none',
                boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
                '&:hover': {
                  boxShadow: '0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)',
                }
              }}
            >
              Try InboxIQ
            </Button>
            <Button
              component={RouterLink}
              to="/login"
              variant="outlined"
              size="large"
              sx={{
                px: 4,
                py: 1.5,
                fontSize: '1.1rem',
                fontWeight: 500,
                borderRadius: '24px',
                textTransform: 'none',
                borderColor: '#dadce0',
                color: '#1a73e8',
                '&:hover': {
                  backgroundColor: '#f8f9fa',
                  borderColor: '#dadce0'
                }
              }}
            >
              Sign In
            </Button>
          </Box>

          {/* Status Chips */}
          <Box sx={{ mt: 4, display: 'flex', gap: 1, justifyContent: 'center', flexWrap: 'wrap' }}>
            <Chip
              label="✨ Powered by Gemini 2.5 Flash"
              sx={{
                backgroundColor: '#e8f0fe',
                color: '#1a73e8',
                fontWeight: 500,
                '& .MuiChip-label': { px: 2 }
              }}
            />
            <Chip
              label="🔒 OAuth2 Secure"
              sx={{
                backgroundColor: '#e6f4ea',
                color: '#137333',
                fontWeight: 500,
                '& .MuiChip-label': { px: 2 }
              }}
            />
            <Chip
              label="⚡ Redis Powered"
              sx={{
                backgroundColor: '#fef7e0',
                color: '#ea8600',
                fontWeight: 500,
                '& .MuiChip-label': { px: 2 }
              }}
            />
          </Box>
        </Box>
      </Container>

      {/* Features Section */}
      <Container maxWidth="lg" sx={{ pb: 8 }}>
        <Typography
          variant="h3"
          component="h2"
          sx={{
            textAlign: 'center',
            mb: 6,
            fontWeight: 400,
            color: '#202124',
            fontFamily: 'Google Sans, Roboto, sans-serif'
          }}
        >
          Everything you need for smarter email management
        </Typography>

        <Grid container spacing={4}>
          {features.map((feature, index) => (
            <Grid xs={12} md={6} lg={4} key={index}>
              <Card
                sx={{
                  height: '100%',
                  border: '1px solid #e0e0e0',
                  borderRadius: '12px',
                  boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
                  transition: 'all 0.2s ease',
                  '&:hover': {
                    boxShadow: '0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)',
                    transform: 'translateY(-2px)'
                  }
                }}
              >
                <CardContent sx={{ p: 4 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <Avatar
                      sx={{
                        backgroundColor: `${feature.color}15`,
                        width: 56,
                        height: 56,
                        mr: 2
                      }}
                    >
                      {feature.icon}
                    </Avatar>
                  </Box>
                  <Typography
                    variant="h6"
                    component="h3"
                    sx={{
                      fontWeight: 500,
                      color: '#202124',
                      mb: 2,
                      fontFamily: 'Google Sans, Roboto, sans-serif'
                    }}
                  >
                    {feature.title}
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: '#5f6368',
                      lineHeight: 1.6
                    }}
                  >
                    {feature.description}
                  </Typography>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      </Container>

      {/* CTA Section */}
      <Box sx={{ backgroundColor: '#ffffff', py: 8 }}>
        <Container maxWidth="md">
          <Box sx={{ textAlign: 'center' }}>
            <Typography
              variant="h3"
              component="h2"
              sx={{
                fontWeight: 400,
                color: '#202124',
                mb: 3,
                fontFamily: 'Google Sans, Roboto, sans-serif'
              }}
            >
              Ready to transform your email workflow?
            </Typography>
            <Typography
              variant="h6"
              sx={{
                color: '#5f6368',
                mb: 4,
                fontWeight: 400
              }}
            >
              Join thousands of professionals who trust InboxIQ for smarter email management.
            </Typography>
            <Button
              component={RouterLink}
              to="/register"
              variant="contained"
              size="large"
              sx={{
                px: 6,
                py: 2,
                fontSize: '1.2rem',
                fontWeight: 500,
                borderRadius: '24px',
                textTransform: 'none',
                boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
                '&:hover': {
                  boxShadow: '0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)',
                }
              }}
            >
              Get Started Free
            </Button>
          </Box>
        </Container>
      </Box>
    </Box>
  )
}
