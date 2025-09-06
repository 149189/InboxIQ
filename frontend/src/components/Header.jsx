// src/components/Header.jsx
import React from 'react'
import AppBar from '@mui/material/AppBar'
import Toolbar from '@mui/material/Toolbar'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import Container from '@mui/material/Container'
import { Link as RouterLink } from 'react-router-dom'

export default function Header() {
  return (
    <AppBar position="static" color="primary" enableColorOnDark>
      <Container maxWidth="lg">
        <Toolbar disableGutters sx={{ display: 'flex', justifyContent: 'space-between' }}>
          <Typography
            variant="h6"
            component={RouterLink}
            to="/"
            sx={{ textDecoration: 'none', color: 'inherit', fontWeight: 700 }}
          >
            InboxIQ
          </Typography>

          <div>
            <Button component={RouterLink} to="/" color="inherit">Home</Button>
            <Button component={RouterLink} to="/login" color="inherit">Login</Button>
          </div>
        </Toolbar>
      </Container>
    </AppBar>
  )
}
