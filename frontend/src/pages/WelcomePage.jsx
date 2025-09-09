// src/pages/WelcomePage.jsx
import React from 'react'
import Container from '@mui/material/Container'
import Paper from '@mui/material/Paper'
import Typography from '@mui/material/Typography'
import Button from '@mui/material/Button'
import Grid from '@mui/material/Grid'
import Box from '@mui/material/Box'
import { Link as RouterLink } from 'react-router-dom'

export default function WelcomePage() {
  return (
    <Container maxWidth="lg" sx={{ py: 8 }}>
      <Paper elevation={2} sx={{ p: { xs: 4, md: 6 }, mb: 4 }}>
        <Typography variant="h3" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
          Welcome to InboxIQ
        </Typography>

        <Typography variant="h6" color="text.secondary" paragraph>
          An AI Agent that takes user prompt and converts it to a polished email drafts and sends it with a short term memory and safe gmail draft integration
        </Typography>

        <Box sx={{ mt: 2, display: 'flex', gap: 2 }}>
          <Button variant="contained" component={RouterLink} to="/login">Login</Button>
          <Button variant="outlined" component={RouterLink} to="/register">Get Started</Button>
        </Box>
      </Paper>

      <Grid container spacing={2}>
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6">Polished Drafts</Typography>
            <Typography variant="body2" color="text.secondary">Transform rough prompts into professional email drafts in one click.</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6">Short-term Memory</Typography>
            <Typography variant="body2" color="text.secondary">Context-awareness across a session so follow-up prompts stay coherent.</Typography>
          </Paper>
        </Grid>
        <Grid item xs={12} md={4}>
          <Paper variant="outlined" sx={{ p: 3 }}>
            <Typography variant="h6">Safe Gmail Drafts</Typography>
            <Typography variant="body2" color="text.secondary">Integrates with Gmail drafts safely — no unexpected sends unless confirmed.</Typography>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  )
}
