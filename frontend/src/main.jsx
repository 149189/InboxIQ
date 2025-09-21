import React from 'react'
import { createRoot } from 'react-dom/client'
import App from './App'
import CssBaseline from '@mui/material/CssBaseline'
import { ThemeProvider } from '@mui/material/styles'
import googleTheme from './theme/googleTheme'

createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <ThemeProvider theme={googleTheme}>
      <CssBaseline />
      <App />
    </ThemeProvider>
  </React.StrictMode>
)
