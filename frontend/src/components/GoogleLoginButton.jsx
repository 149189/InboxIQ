// src/components/GoogleLoginButton.jsx
import React, { useState } from 'react'
import Button from '@mui/material/Button'

/**
 * GoogleLoginButton
 *
 * - Fetches the backend oauth start endpoint which returns { auth_url, state }.
 * - Uses credentials: 'include' so the Django session cookie (and saved oauth_state) is set.
 * - Redirects the browser to Google (auth_url) on success.
 *
 * NOTE:
 * - If you use a Vite proxy mapping '/accounts' -> 'http://127.0.0.1:8000',
 *   you can change BACKEND_OAUTH_START to '/accounts/oauth/google/login/'.
 * - Django must allow CORS credentials if frontend is on another origin:
 *   CORS_ALLOW_CREDENTIALS = True and CORS_ALLOWED_ORIGINS include your frontend origin.
 */

const BACKEND_OAUTH_START = 'http://127.0.0.1:8000/accounts/oauth/google/login/'

export default function GoogleLoginButton({ children = 'Continue with Google', variant = 'contained' }) {
  const [loading, setLoading] = useState(false)

  const handleClick = async () => {
    setLoading(true)
    try {
      const res = await fetch(BACKEND_OAUTH_START, {
        method: 'GET',
        credentials: 'include', // important: lets Django set session cookie for state verification
        headers: {
          'Accept': 'application/json',
        },
      })

      if (!res.ok) {
        const txt = await res.text().catch(() => '')
        throw new Error(`Server returned ${res.status} ${res.statusText} ${txt ? `: ${txt}` : ''}`)
      }

      const data = await res.json()
      if (data?.auth_url) {
        // Redirect the whole window to Google OAuth URL
        window.location.href = data.auth_url
      } else {
        throw new Error('No auth_url returned from server')
      }
    } catch (err) {
      console.error('OAuth start error:', err)
      // user-friendly message
      alert('Failed to start Google sign-in. See console for details.')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Button
      variant={variant}
      onClick={handleClick}
      disabled={loading}
    >
      {loading ? 'Starting...' : children}
    </Button>
  )
}
