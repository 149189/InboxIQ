// src/App.jsx
import React from 'react'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

import Header from './components/Header'
import Footer from './components/Footer'

import WelcomePage from './pages/WelcomePage'
import LoginPage from './pages/LoginPage'
import RegisterPage from './pages/RegisterPage'
import OAuthCallbackPage from './pages/OAuthCallbackPage'
import CalendarPage from './pages/CalendarPage'
import UnifiedChatPage from './pages/UnifiedChatPage'

import GoogleLoginButton from './components/GoogleLoginButton'
import Chat from './pages/Chat' 

function GoogleLoginPage() {
  return (
    <div style={{ maxWidth: 1100, margin: '0 auto', padding: '2rem' }}>
      <h1 style={{ marginBottom: '1rem' }}>Sign in with Google</h1>
      <GoogleLoginButton />
    </div>
  )
}

// Component to handle OAuth redirects that hit the frontend by mistake
function OAuthRedirectHandler() {
  React.useEffect(() => {
    // Redirect to the correct backend URL with all query parameters
    const currentUrl = new URL(window.location.href)
    const backendUrl = `http://127.0.0.1:8000/auth${currentUrl.pathname}${currentUrl.search}`
    
    console.log('Redirecting OAuth callback to backend:', backendUrl)
    window.location.replace(backendUrl)
  }, [])

  return (
    <div style={{ padding: '2rem', textAlign: 'center' }}>
      <p>Redirecting OAuth callback to backend...</p>
    </div>
  )
}

export default function App() {
  return (
    <BrowserRouter>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', backgroundColor: '#f8f9fa' }}>
        <Header />
        <main style={{ flex: 1 }}>
          <Routes>
            <Route path="/" element={<WelcomePage />} />
            <Route path="/login" element={<LoginPage />} />
            <Route path="/register" element={<RegisterPage />} />
            <Route path="/oauth/callback" element={<OAuthCallbackPage />} />
            <Route path="/oauth/google/callback" element={<OAuthRedirectHandler />} />
            <Route path="/google-login" element={<GoogleLoginPage />} />
            <Route path="/chat" element={<UnifiedChatPage />} />
            <Route path="/calendar" element={<CalendarPage />} />
            <Route path="/gmail" element={<Chat />} />
          </Routes>
        </main>
        <Footer />
      </div>
    </BrowserRouter>
  )
}