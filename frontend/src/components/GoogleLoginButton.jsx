// src/components/GoogleLoginButton.jsx
import React, { useState } from 'react'
import Button from '@mui/material/Button'

/**
 * GoogleLoginButton (updated)
 *
 * - Uses a top-level navigation to the backend start endpoint instead of fetch.
 *   This ensures the backend's Set-Cookie (sessionid) is handled as a regular
 *   navigation response and will be present when Google redirects back.
 *
 * - BACKEND_OAUTH_START should point to your backend start URL that returns a
 *   redirect to Google's auth endpoint (and sets the session cookie).
 *
 * - If you prefer opening the flow in a new tab, set openInNewTab={true} on the component.
 */

const BACKEND_OAUTH_START = 'http://127.0.0.1:8000/auth/oauth/google/login/'

export default function GoogleLoginButton({
  children = 'Continue with Google',
  variant = 'contained',
  openInNewTab = false,
}) {
  const [starting, setStarting] = useState(false)

  const handleClick = () => {
    setStarting(true)

    // Use top-level navigation so Set-Cookie is applied correctly.
    // We use assign() so the navigation appears in history (back button works).
    // Optionally open in a new tab/window if requested.
    try {
      if (openInNewTab) {
        window.open(BACKEND_OAUTH_START, '_blank', 'noopener,noreferrer')
      } else {
        // small timeout so loading state renders before navigation (optional)
        setTimeout(() => {
          window.location.assign(BACKEND_OAUTH_START)
        }, 150)
      }
    } catch (err) {
      console.error('Failed to start OAuth navigation:', err)
      alert('Failed to start Google sign-in. See console for details.')
      setStarting(false)
    }
  }

  return (
    <Button onClick={handleClick} variant={variant} disabled={starting}>
      {starting ? 'Starting…' : children}
    </Button>
  )
}
