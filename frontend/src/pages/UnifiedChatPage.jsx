// src/pages/UnifiedChatPage.jsx
import React, { useState, useEffect } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Card,
  CardContent,
  Avatar,
  Chip,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Menu,
  MenuItem,
  Divider,
  Button,
  TextField,
  Grid
} from '@mui/material';
import {
  Person as PersonIcon,
  SmartToy as BotIcon,
  Email as EmailIcon,
  CalendarToday as CalendarIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Edit as EditIcon,
  Settings as SettingsIcon,
  AccountCircle as AccountCircleIcon,
  Logout as LogoutIcon,
  AutoAwesome as AIIcon
} from '@mui/icons-material';
import { useNavigate, Link as RouterLink } from 'react-router-dom';
import UnifiedChat from '../components/UnifiedChat';
import { CalendarProvider, useCalendar } from '../contexts/CalendarContext';
import calendarService from '../services/calendarService';

// Gmail service functions (existing functionality)
const startGmailSession = async () => {
  const response = await fetch('http://localhost:8000/api/chat/start/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Failed to start Gmail session');
  return response.json();
};

const sendGmailMessage = async (sessionId, message) => {
  const response = await fetch('http://localhost:8000/api/chat/send/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    credentials: 'include',
    body: JSON.stringify({ session_id: sessionId, message }),
  });
  if (!response.ok) throw new Error('Failed to send Gmail message');
  return response.json();
};

const getGmailHistory = async (sessionId) => {
  const response = await fetch(`http://localhost:8000/api/chat/history/${sessionId}/`, {
    credentials: 'include',
  });
  if (!response.ok) throw new Error('Failed to get Gmail history');
  return response.json();
};

function UnifiedChatContent() {
  // Gmail state
  const [gmailMessages, setGmailMessages] = useState([]);
  const [gmailSessionId, setGmailSessionId] = useState(null);
  const [gmailLoading, setGmailLoading] = useState(false);
  const [gmailError, setGmailError] = useState(null);

  // Calendar state from context
  const {
    messages: calendarMessages,
    isLoading: calendarLoading,
    error: calendarError,
    startSession: startCalendarSession,
    sendMessage: sendCalendarMessage,
    loadHistory: loadCalendarHistory
  } = useCalendar();

  // User profile state
  const [userProfile, setUserProfile] = useState(null);
  const [profileSetupDialog, setProfileSetupDialog] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [emailConfirmDialog, setEmailConfirmDialog] = useState(null);
  const [isSessionSyncing, setIsSessionSyncing] = useState(false);
  const navigate = useNavigate();

  // Initialize sessions
  useEffect(() => {
    // Check if this is an OAuth callback
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('oauth_success') === 'true') {
      // OAuth callback - sync session first, then fetch profile
      if (!isSessionSyncing) {
        syncSessionAfterOAuth();
      }
    } else {
      // Normal page load - just fetch profile
      fetchUserProfile();
    }
  }, []);

  // Initialize sessions when user profile is loaded
  useEffect(() => {
    if (userProfile) {
      initializeSessions();
    }
  }, [userProfile]);

  const initializeSessions = async () => {
    // Only initialize sessions if user is authenticated
    if (!userProfile) {
      console.log('User not authenticated - skipping session initialization');
      return;
    }

    try {
      // Start Gmail session
      const gmailSession = await startGmailSession();
      setGmailSessionId(gmailSession.session_id);
      
      if (gmailSession.message) {
        setGmailMessages([{
          id: gmailSession.message.id,
          type: gmailSession.message.type,
          content: gmailSession.message.content,
          timestamp: gmailSession.message.timestamp,
          metadata: gmailSession.message.metadata || {}
        }]);
      }

      // Start Calendar session
      await startCalendarSession();
    } catch (error) {
      console.error('Failed to initialize sessions:', error);
      setGmailError('Failed to initialize chat sessions');
    }
  };

  const syncSessionAfterOAuth = async () => {
    // Prevent duplicate calls in React StrictMode
    if (isSessionSyncing) {
      console.log('Session sync already in progress, skipping...');
      return;
    }

    try {
      setIsSessionSyncing(true);
      console.log('Syncing session after OAuth...');
      const response = await fetch('http://localhost:8000/auth/sync-session/', {
        credentials: 'include',
      });
      if (response.ok) {
        const data = await response.json();
        console.log('Session synced successfully:', data);
        
        // Manually set the session cookie if it's not being set automatically
        if (data.session_key) {
          document.cookie = `sessionid=${data.session_key}; path=/; SameSite=None; Secure=false`;
          console.log('Manually set session cookie:', data.session_key);
        }
        
        // Clean up URL parameters
        window.history.replaceState({}, document.title, window.location.pathname);
        
        // Add a small delay to ensure cookie is set before next request
        await new Promise(resolve => setTimeout(resolve, 200));
        
        // Test session with debug endpoint first
        console.log('Testing session with debug endpoint...');
        try {
          const debugResponse = await fetch('http://localhost:8000/auth/session-test/', {
            credentials: 'include',
          });
          const debugData = await debugResponse.json();
          console.log('Session debug data:', debugData);
        } catch (error) {
          console.error('Session debug failed:', error);
        }
        
        // Now fetch user profile
        fetchUserProfile();
      } else {
        console.error('Failed to sync session:', response.status);
        // Fallback to normal profile fetch
        fetchUserProfile();
      }
    } catch (error) {
      console.error('Error syncing session:', error);
      // Fallback to normal profile fetch
      fetchUserProfile();
    } finally {
      setIsSessionSyncing(false);
    }
  };

  const fetchUserProfile = async () => {
    try {
      console.log('Fetching user profile...');
      console.log('Current cookies:', document.cookie);
      
      const response = await fetch('http://localhost:8000/auth/oauth/profile/', {
        credentials: 'include',
      });
      
      console.log('Profile response status:', response.status);
      
      if (response.ok) {
        const profile = await response.json();
        console.log('Profile loaded successfully:', profile);
        setUserProfile(profile);
      } else if (response.status === 401) {
        // User not authenticated - this is expected for the welcome page
        console.log('User not authenticated - showing welcome page');
        setUserProfile(null);
      }
    } catch (error) {
      console.error('Failed to fetch user profile:', error);
      setUserProfile(null);
    }
  };

  const handleGmailMessage = async (message) => {
    if (!gmailSessionId) {
      throw new Error('Gmail session not initialized');
    }

    setGmailLoading(true);
    setGmailError(null);

    try {
      // Add user message immediately
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: message,
        timestamp: new Date().toISOString(),
        metadata: {}
      };
      setGmailMessages(prev => [...prev, userMessage]);

      // Send to backend
      const response = await sendGmailMessage(gmailSessionId, message);
      
      // Add assistant response
      if (response.message) {
        setGmailMessages(prev => [...prev, {
          id: response.message.id,
          type: response.message.type,
          content: response.message.content,
          timestamp: response.message.timestamp,
          metadata: response.message.metadata || {}
        }]);

        // Handle email confirmation dialog
        if (response.message.metadata?.drafts) {
          setEmailConfirmDialog({
            drafts: response.message.metadata.drafts,
            sessionId: gmailSessionId
          });
        }
      }
    } catch (error) {
      setGmailError(error.message);
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `I'm sorry, I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date().toISOString(),
        metadata: { isError: true }
      };
      setGmailMessages(prev => [...prev, errorMessage]);
    } finally {
      setGmailLoading(false);
    }
  };

  const handleCalendarMessage = async (message) => {
    try {
      await sendCalendarMessage(message);
    } catch (error) {
      console.error('Calendar message error:', error);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch('http://localhost:8000/auth/logout/', {
        method: 'POST',
        credentials: 'include',
      });
      navigate('/');
    } catch (error) {
      console.error('Logout error:', error);
    }
  };

  return (
    <Box sx={{ minHeight: '100vh', bgcolor: '#f8f9fa' }}>
      {/* Header */}
      <Box
        sx={{
          bgcolor: 'linear-gradient(135deg, #4285f4 0%, #ea4335 100%)',
          background: 'linear-gradient(135deg, #4285f4 0%, #ea4335 100%)',
          color: 'white',
          py: 3
        }}
      >
        <Container maxWidth="xl">
          <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <Box sx={{ display: 'flex', alignItems: 'center' }}>
              <Avatar
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  width: 48,
                  height: 48,
                  mr: 2
                }}
              >
                <AIIcon sx={{ fontSize: 24 }} />
              </Avatar>
              
              <Box>
                <Typography
                  variant="h4"
                  component="h1"
                  sx={{
                    fontWeight: 400,
                    fontFamily: 'Google Sans, Roboto, sans-serif'
                  }}
                >
                  InboxIQ Assistant
                </Typography>
                <Typography
                  variant="subtitle1"
                  sx={{
                    fontWeight: 400,
                    opacity: 0.9
                  }}
                >
                  AI-powered email and calendar management
                </Typography>
              </Box>
            </Box>

            {/* User Menu */}
            {userProfile && (
              <Box>
                <IconButton
                  onClick={(e) => setUserMenuAnchor(e.currentTarget)}
                  sx={{ color: 'white' }}
                >
                  <Avatar
                    src={userProfile.profile_picture}
                    sx={{ width: 40, height: 40 }}
                  >
                    {userProfile.display_name?.[0] || userProfile.username?.[0] || 'U'}
                  </Avatar>
                </IconButton>
                
                <Menu
                  anchorEl={userMenuAnchor}
                  open={Boolean(userMenuAnchor)}
                  onClose={() => setUserMenuAnchor(null)}
                >
                  <MenuItem onClick={() => setProfileSetupDialog(true)}>
                    <SettingsIcon sx={{ mr: 1 }} />
                    Profile Settings
                  </MenuItem>
                  <Divider />
                  <MenuItem onClick={handleLogout}>
                    <LogoutIcon sx={{ mr: 1 }} />
                    Logout
                  </MenuItem>
                </Menu>
              </Box>
            )}
          </Box>

          {/* Feature Chips */}
          <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, flexWrap: 'wrap', mt: 2 }}>
            <Chip
              label="✨ Powered by Gemini 2.5 Flash"
              sx={{
                bgcolor: 'rgba(255,255,255,0.2)',
                color: 'white',
                fontWeight: 500
              }}
            />
            <Chip
              label="📧 Gmail Integration"
              sx={{
                bgcolor: 'rgba(255,255,255,0.2)',
                color: 'white',
                fontWeight: 500
              }}
            />
            <Chip
              label="📅 Calendar Management"
              sx={{
                bgcolor: 'rgba(255,255,255,0.2)',
                color: 'white',
                fontWeight: 500
              }}
            />
            <Chip
              label="🤖 Intelligent Routing"
              sx={{
                bgcolor: 'rgba(255,255,255,0.2)',
                color: 'white',
                fontWeight: 500
              }}
            />
          </Box>
        </Container>
      </Box>

      <Container maxWidth="xl" sx={{ py: 4 }}>
        <Grid container spacing={4}>
          {/* Features Section */}
          <Grid size={{ xs: 12, lg: 3 }}>
            <Typography
              variant="h6"
              sx={{
                fontWeight: 500,
                mb: 2,
                color: '#202124',
                fontFamily: 'Google Sans, Roboto, sans-serif'
              }}
            >
              What I Can Help You With
            </Typography>

            <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
              <Card elevation={0} sx={{ border: '1px solid #e0e0e0', borderRadius: 2 }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <EmailIcon sx={{ color: '#ea4335', mr: 1 }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
                      Email Management
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: '#5f6368', fontSize: '0.875rem' }}>
                    Draft emails, manage inbox, send messages
                  </Typography>
                </CardContent>
              </Card>

              <Card elevation={0} sx={{ border: '1px solid #e0e0e0', borderRadius: 2 }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <CalendarIcon sx={{ color: '#4285f4', mr: 1 }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
                      Calendar Scheduling
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: '#5f6368', fontSize: '0.875rem' }}>
                    Create events, find free time, manage schedule
                  </Typography>
                </CardContent>
              </Card>

              <Card elevation={0} sx={{ border: '1px solid #e0e0e0', borderRadius: 2 }}>
                <CardContent sx={{ p: 2 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <AIIcon sx={{ color: '#34a853', mr: 1 }} />
                    <Typography variant="subtitle2" sx={{ fontWeight: 500 }}>
                      Smart Detection
                    </Typography>
                  </Box>
                  <Typography variant="body2" sx={{ color: '#5f6368', fontSize: '0.875rem' }}>
                    Automatically routes to email or calendar
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          </Grid>

          {/* Chat Section */}
          <Grid size={{ xs: 12, lg: 9 }}>
            <Paper
              elevation={0}
              sx={{
                height: '700px',
                border: '1px solid #e0e0e0',
                borderRadius: 2,
                overflow: 'hidden',
                display: 'flex',
                flexDirection: 'column'
              }}
            >
              {userProfile ? (
                <UnifiedChat
                  onGmailMessage={handleGmailMessage}
                  onCalendarMessage={handleCalendarMessage}
                  gmailMessages={gmailMessages}
                  calendarMessages={calendarMessages}
                  isLoading={gmailLoading || calendarLoading}
                  error={gmailError || calendarError}
                />
              ) : (
                <Box
                  sx={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    height: '100%',
                    p: 4,
                    textAlign: 'center'
                  }}
                >
                  <Avatar
                    sx={{
                      width: 80,
                      height: 80,
                      backgroundColor: '#4285f4',
                      mb: 3
                    }}
                  >
                    <AIIcon sx={{ fontSize: '2.5rem' }} />
                  </Avatar>
                  <Typography
                    variant="h5"
                    sx={{
                      color: '#202124',
                      mb: 2,
                      fontFamily: 'Google Sans, Roboto, sans-serif',
                      fontWeight: 400
                    }}
                  >
                    Welcome to InboxIQ
                  </Typography>
                  <Typography
                    variant="body1"
                    sx={{
                      color: '#5f6368',
                      mb: 4,
                      maxWidth: '400px'
                    }}
                  >
                    Please sign in to start using your AI-powered email and calendar assistant.
                  </Typography>
                  <Button
                    component={RouterLink}
                    to="/login"
                    variant="contained"
                    size="large"
                    sx={{
                      px: 4,
                      py: 1.5,
                      fontSize: '1rem',
                      fontWeight: 500,
                      borderRadius: '24px',
                      textTransform: 'none'
                    }}
                  >
                    Sign In to Continue
                  </Button>
                </Box>
              )}
            </Paper>
          </Grid>
        </Grid>
      </Container>

      {/* Email Confirmation Dialog */}
      {emailConfirmDialog && (
        <Dialog
          open={true}
          onClose={() => setEmailConfirmDialog(null)}
          maxWidth="md"
          fullWidth
        >
          <DialogTitle>Review Email Drafts</DialogTitle>
          <DialogContent>
            <Typography variant="body2" sx={{ mb: 2, color: '#5f6368' }}>
              I've created {emailConfirmDialog.drafts.length} email draft{emailConfirmDialog.drafts.length > 1 ? 's' : ''} for you. 
              Review and choose which one to save to Gmail.
            </Typography>
            
            {emailConfirmDialog.drafts.map((draft, index) => (
              <Paper
                key={index}
                elevation={0}
                sx={{
                  p: 2,
                  mb: 2,
                  border: '1px solid #e0e0e0',
                  borderRadius: 1
                }}
              >
                <Typography variant="subtitle2" sx={{ fontWeight: 500, mb: 1 }}>
                  Draft {index + 1}
                </Typography>
                <Typography
                  variant="body2"
                  sx={{
                    whiteSpace: 'pre-wrap',
                    fontFamily: 'monospace',
                    bgcolor: '#f8f9fa',
                    p: 1,
                    borderRadius: 1
                  }}
                >
                  {draft}
                </Typography>
              </Paper>
            ))}
          </DialogContent>
          <DialogActions>
            <Button onClick={() => setEmailConfirmDialog(null)}>
              Cancel
            </Button>
            <Button variant="contained" onClick={() => setEmailConfirmDialog(null)}>
              Save to Gmail
            </Button>
          </DialogActions>
        </Dialog>
      )}
    </Box>
  );
}

export default function UnifiedChatPage() {
  return (
    <CalendarProvider>
      <UnifiedChatContent />
    </CalendarProvider>
  );
}
