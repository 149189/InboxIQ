// src/pages/Dashboard.jsx
import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import Box from '@mui/material/Box'
import Avatar from '@mui/material/Avatar'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import CircularProgress from '@mui/material/CircularProgress'
import Paper from '@mui/material/Paper'
import Stack from '@mui/material/Stack'

const PROFILE_URL = 'http://127.0.0.1:8000/auth/oauth/profile/'
const LOGOUT_URL = 'http://127.0.0.1:8000/auth/logout/'

export default function Dashboard() {
  const [loading, setLoading] = useState(true)
  const [profile, setProfile] = useState(null)
  const [error, setError] = useState(null)
  const navigate = useNavigate()

  useEffect(() => {
    let mounted = true
    const fetchProfile = async () => {
      setLoading(true)
      setError(null)
      try {
        const res = await fetch(PROFILE_URL, {
          method: 'GET',
          credentials: 'include',
          headers: { Accept: 'application/json' }
        })

        if (res.status === 401) {
          // not authenticated — go to login
          if (mounted) navigate('/login')
          return
        }

        if (!res.ok) {
          const txt = await res.text().catch(() => '')
          throw new Error(`Failed to load profile (${res.status}) ${txt}`)
        }

        const data = await res.json()
        if (mounted) setProfile(data)
      } catch (err) {
        console.error('Profile fetch error:', err)
        if (mounted) setError(err.message || 'Failed to load profile')
      } finally {
        if (mounted) setLoading(false)
      }
    }

    fetchProfile()
    return () => { mounted = false }
  }, [navigate])

  const handleLogout = async () => {
    try {
      const res = await fetch(LOGOUT_URL, {
        method: 'POST',
        credentials: 'include',
        headers: { 'Content-Type': 'application/json' },
      })
      if (!res.ok) {
        const txt = await res.text().catch(() => '')
        throw new Error(`Logout failed (${res.status}) ${txt}`)
      }
      // go back to home after logout
      navigate('/')
    } catch (err) {
      console.error(err)
      alert('Logout failed — check console')
    }
  }

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', mt: 8 }}>
        <CircularProgress />
      </Box>
    )
  }

  if (error) {
    return (
      <Box sx={{ maxWidth: 800, mx: 'auto', mt: 8 }}>
        <Paper sx={{ p: 4 }}>
          <Typography variant="h6" color="error">Error</Typography>
          <Typography variant="body2" sx={{ mt: 1 }}>{error}</Typography>
          <Button sx={{ mt: 2 }} variant="contained" onClick={() => window.location.reload()}>Retry</Button>
        </Paper>
      </Box>
    )
  }

  if (!profile) {
    return null
  }

  return (
    <Box sx={{ maxWidth: 900, mx: 'auto', px: 2, py: 6 }}>
      <Paper sx={{ p: { xs: 3, md: 6 } }}>
        <Stack direction={{ xs: 'column', md: 'row' }} spacing={4} alignItems="center">
          <Avatar
            alt={profile.full_name || profile.username}
            src={profile.profile_picture || ''}
            sx={{ width: 96, height: 96 }}
          />
          <Box sx={{ flex: 1 }}>
            <Typography variant="h4" component="h1">
              Hello, {profile.full_name || profile.username} 👋
            </Typography>
            {profile.email && <Typography color="text.secondary" sx={{ mt: 1 }}>{profile.email}</Typography>}
            <Typography variant="body2" sx={{ mt: 1, color: 'text.secondary' }}>
              Joined: {profile.date_joined ? new Date(profile.date_joined).toLocaleString() : '—'}
            </Typography>
          </Box>

          <Box>
            <Button variant="contained" color="primary" onClick={() => navigate('/')} sx={{ mr: 2 }}>
              Home
            </Button>
            <Button variant="outlined" color="error" onClick={handleLogout}>Logout</Button>
          </Box>
        </Stack>
      </Paper>

      {/* Optional profile raw JSON for debugging */}
      <Box sx={{ mt: 4 }}>
        <Paper sx={{ p: 2, backgroundColor: '#fafafa' }}>
          <Typography variant="subtitle2">Session profile (debug)</Typography>
          <pre style={{ whiteSpace: 'pre-wrap', fontSize: 12 }}>{JSON.stringify(profile, null, 2)}</pre>
        </Paper>
      </Box>
    </Box>
  )
}
