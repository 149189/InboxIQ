// src/components/Header.jsx
import React from 'react'
import {
  AppBar,
  Toolbar,
  Typography,
  Button,
  Container,
  Box,
  IconButton,
  Avatar
} from '@mui/material'
import {
  Apps as AppsIcon,
  AccountCircle as AccountCircleIcon
} from '@mui/icons-material'
import { Link as RouterLink, useLocation } from 'react-router-dom'

export default function Header() {
  const location = useLocation()

  return (
    <AppBar 
      position="static" 
      elevation={0}
      sx={{ 
        backgroundColor: '#ffffff',
        borderBottom: '1px solid #e0e0e0',
        color: '#202124'
      }}
    >
      <Container maxWidth="xl">
        <Toolbar 
          disableGutters 
          sx={{ 
            display: 'flex', 
            justifyContent: 'space-between',
            minHeight: '64px !important',
            py: 1
          }}
        >
          {/* Logo Section */}
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <Typography
              variant="h5"
              component={RouterLink}
              to="/"
              sx={{ 
                textDecoration: 'none', 
                color: '#202124',
                fontWeight: 400,
                fontFamily: 'Google Sans, Roboto, sans-serif',
                display: 'flex',
                alignItems: 'center',
                '&:hover': {
                  textDecoration: 'none'
                }
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
          </Box>

          {/* Navigation Section */}
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Button
              component={RouterLink}
              to="/"
              sx={{
                color: location.pathname === '/' ? '#1a73e8' : '#5f6368',
                textTransform: 'none',
                fontWeight: 500,
                px: 2,
                py: 1,
                borderRadius: '24px',
                '&:hover': {
                  backgroundColor: '#f1f3f4',
                  color: '#202124'
                }
              }}
            >
              Home
            </Button>
            
            <Button
              component={RouterLink}
              to="/chat"
              sx={{
                color: location.pathname === '/chat' ? '#1a73e8' : '#5f6368',
                textTransform: 'none',
                fontWeight: 500,
                px: 2,
                py: 1,
                borderRadius: '24px',
                '&:hover': {
                  backgroundColor: '#f1f3f4',
                  color: '#202124'
                }
              }}
            >
              Chat
            </Button>

            <Button
              component={RouterLink}
              to="/calendar"
              sx={{
                color: location.pathname === '/calendar' ? '#1a73e8' : '#5f6368',
                textTransform: 'none',
                fontWeight: 500,
                px: 2,
                py: 1,
                borderRadius: '24px',
                '&:hover': {
                  backgroundColor: '#f1f3f4',
                  color: '#202124'
                }
              }}
            >
              Calendar
            </Button>

            {/* Google Apps Icon */}
            <IconButton
              sx={{
                color: '#5f6368',
                ml: 1,
                '&:hover': {
                  backgroundColor: '#f1f3f4'
                }
              }}
            >
              <AppsIcon />
            </IconButton>

            {/* Sign In Button */}
            <Button
              component={RouterLink}
              to="/login"
              variant="outlined"
              sx={{
                textTransform: 'none',
                fontWeight: 500,
                borderColor: '#dadce0',
                color: '#1a73e8',
                px: 3,
                py: 1,
                ml: 1,
                borderRadius: '24px',
                '&:hover': {
                  backgroundColor: '#f8f9fa',
                  borderColor: '#dadce0'
                }
              }}
            >
              Sign in
            </Button>

            {/* Profile Avatar (when logged in) */}
            <IconButton
              sx={{
                ml: 1,
                '&:hover': {
                  backgroundColor: '#f1f3f4'
                }
              }}
            >
              <Avatar
                sx={{
                  width: 32,
                  height: 32,
                  backgroundColor: '#1a73e8',
                  fontSize: '0.875rem'
                }}
              >
                <AccountCircleIcon />
              </Avatar>
            </IconButton>
          </Box>
        </Toolbar>
      </Container>
    </AppBar>
  )
}
