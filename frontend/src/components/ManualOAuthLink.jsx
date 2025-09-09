import React from 'react'
import Link from '@mui/material/Link'
import Typography from '@mui/material/Typography'

export default function ManualOAuthLink() {
  return (
    <Typography variant="body2" sx={{ mt: 2 }}>
      If the button doesn't work,{' '}
      <Link 
        href="/oauth/google/login/" 
        onClick={(e) => {
          e.preventDefault();
          window.location.href = '/oauth/google/login/';
        }}
      >
        click here to sign in with Google
      </Link>
    </Typography>
  )
}