// src/components/GoogleOAuthButton.jsx
import React, { useState } from 'react'
import Button from '@mui/material/Button'

const BACKEND_OAUTH_START = 'http://127.0.0.1:8000/auth/oauth/google/login/'

export default function GoogleOAuthButton({
  children = 'Continue with Google',
  variant = 'contained',
}) {
  const [starting, setStarting] = useState(false)

  const handleClick = () => {
    setStarting(true)
    // Navigate directly to backend start URL
    window.location.href = BACKEND_OAUTH_START
  }

  return (
    <Button variant={variant} onClick={handleClick} disabled={starting}>
      {starting ? 'Starting…' : children}
    </Button>
  )
}
