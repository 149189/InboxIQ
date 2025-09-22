// src/pages/Chat.jsx
import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
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
  Button
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
import { useNavigate } from 'react-router-dom';
import UnifiedChat from '../components/UnifiedChat';
import { CalendarProvider } from '../contexts/CalendarContext';
import calendarService from '../services/calendarService';

export default function Chat() {
  const [gmailMessages, setGmailMessages] = useState([]);
  const [calendarMessages, setCalendarMessages] = useState([]);
  const [gmailSessionId, setGmailSessionId] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [emailConfirmDialog, setEmailConfirmDialog] = useState(null);
  const [userProfile, setUserProfile] = useState(null);
  const [profileSetupDialog, setProfileSetupDialog] = useState(false);
  const [userMenuAnchor, setUserMenuAnchor] = useState(null);
  const [profileForm, setProfileForm] = useState({
    username: '',
    display_name: '',
    profile_picture: ''
  });
  const messagesEndRef = useRef(null);
  const navigate = useNavigate();

  // Auto-scroll to bottom when new messages arrive
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Start chat session and fetch user profile on component mount
  useEffect(() => {
    fetchUserProfile();
  }, []);

  // Start chat session only after user profile is confirmed
  useEffect(() => {
    if (userProfile) {
      startChatSession();
    }
  }, [userProfile]);

  const fetchUserProfile = async () => {
    try {
      const response = await fetch('/auth/sync-session/', {
        method: 'GET',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        console.log('Session sync data:', data);
        
        if (data.authenticated) {
          setUserProfile(data.user);
          
          // Check if profile needs setup (no display name or profile picture)
          if (!data.user.name || data.user.name === data.user.email.split('@')[0]) {
            setProfileSetupDialog(true);
            setProfileForm({
              username: data.user.name || '',
              display_name: '',
              profile_picture: data.user.profile_picture || ''
            });
          }
        } else {
          // User is not authenticated, redirect to login
          console.log('User not authenticated, redirecting to login');
          navigate('/login?error=not_authenticated');
        }
      } else {
        console.error('Failed to sync session:', response.status);
        navigate('/login?error=session_sync_failed');
      }
    } catch (err) {
      console.error('Error fetching user profile:', err);
      navigate('/login?error=profile_fetch_failed');
    }
  };

  const handleProfileUpdate = async () => {
    try {
      setLoading(true);
      const response = await fetch('/auth/update-profile/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileForm)
      });

      if (!response.ok) {
        throw new Error('Failed to update profile');
      }

      const data = await response.json();
      if (data.success) {
        setUserProfile(prev => ({
          ...prev,
          name: data.user.display_name || data.user.username,
          profile_picture: data.user.profile_picture
        }));
        setProfileSetupDialog(false);
        setError(null);
      }
    } catch (err) {
      console.error('Error updating profile:', err);
      setError('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleLogout = async () => {
    try {
      await fetch('/auth/logout/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      sessionStorage.clear();
      localStorage.clear();
      navigate('/login?message=logged_out');
    } catch (err) {
      console.error('Logout failed:', err);
      navigate('/login');
    }
  };

  const startChatSession = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/chat/start/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login?error=session_expired');
          return;
        }
        throw new Error('Failed to start chat session');
      }

      const data = await response.json();
      setSessionId(data.session_id);
      setMessages([data.message]);
    } catch (err) {
      console.error('Error starting chat session:', err);
      setError('Failed to start chat session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const sendMessage = async () => {
    if (!inputMessage.trim() || !sessionId || loading) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: inputMessage.trim(),
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setMessages(prev => [...prev, userMessage]);
    const messageToSend = inputMessage.trim();
    setInputMessage('');
    setLoading(true);

    try {
      const response = await fetch('/api/chat/send/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          message: messageToSend
        })
      });

      if (!response.ok) {
        if (response.status === 401) {
          navigate('/login?error=session_expired');
          return;
        }
        throw new Error('Failed to send message');
      }

      const data = await response.json();
      
      // Add assistant response
      setMessages(prev => [...prev, data.message]);

      // Check if this is an email confirmation
      if (data.message.metadata?.type === 'email_confirmation') {
        setEmailConfirmDialog(data.message.metadata);
      }

    } catch (err) {
      console.error('Error sending message:', err);
      setError('Failed to send message. Please try again.');
      
      // Add error message
      setMessages(prev => [...prev, {
        id: Date.now(),
        type: 'assistant',
        content: 'Sorry, I encountered an error processing your message. Please try again.',
        timestamp: new Date().toISOString()
      }]);
    } finally {
      setLoading(false);
    }
  };

  const handleEmailAction = async (action) => {
    if (!emailConfirmDialog?.draft_id) return;

    try {
      setLoading(true);
      const response = await fetch('/api/email/confirm/', {
        method: 'POST',
        credentials: 'include',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          draft_id: emailConfirmDialog.draft_id,
          action: action
        })
      });

      if (!response.ok) {
        throw new Error('Failed to process email action');
      }

      const data = await response.json();

      if (action === 'send' && data.success) {
        // Add success message
        setMessages(prev => [...prev, {
          id: Date.now(),
          type: 'assistant',
          content: `✅ ${data.message}`,
          timestamp: new Date().toISOString()
        }]);
        setEmailConfirmDialog(null);
      } else if (action === 'cancel') {
        setMessages(prev => [...prev, {
          id: Date.now(),
          type: 'assistant',
          content: 'Email draft cancelled. How else can I help you?',
          timestamp: new Date().toISOString()
        }]);
        setEmailConfirmDialog(null);
      }

    } catch (err) {
      console.error('Error processing email action:', err);
      setError('Failed to process email action. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const formatMessage = (content) => {
    // Simple markdown-like formatting
    return content
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/\n/g, '<br />')
  };

  // Message bubble component with Google-style design
  const MessageBubble = ({ message }) => {
    const isUser = message.message_type === 'user';
    const isEmail = message.metadata?.email_draft;
    
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 3,
          alignItems: 'flex-start',
          px: 2
        }}
      >
        {!isUser && (
          <Avatar 
            sx={{ 
              mr: 2, 
              width: 32, 
              height: 32,
              backgroundColor: '#4285f4',
              fontSize: '1rem'
            }}
          >
            <BotIcon sx={{ fontSize: '1.2rem' }} />
          </Avatar>
        )}
        
        <Box sx={{ maxWidth: '70%', minWidth: '200px' }}>
          <Paper
            elevation={0}
            sx={{
              p: 2.5,
              backgroundColor: isUser ? '#4285f4' : '#ffffff',
              color: isUser ? '#ffffff' : '#202124',
              borderRadius: isUser ? '20px 20px 6px 20px' : '20px 20px 20px 6px',
              border: isUser ? 'none' : '1px solid #e0e0e0',
              boxShadow: isUser 
                ? '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)'
                : '0 1px 2px 0 rgba(60,64,67,0.1)',
              position: 'relative',
              '&::before': isUser ? {} : {
                content: '""',
                position: 'absolute',
                bottom: 0,
                left: -6,
                width: 0,
                height: 0,
                borderLeft: '6px solid transparent',
                borderRight: '6px solid #ffffff',
                borderTop: '6px solid #ffffff',
                borderBottom: '6px solid transparent',
              }
            }}
          >
            <Typography 
              variant="body1" 
              sx={{ 
                lineHeight: 1.5,
                fontSize: '0.95rem',
                fontWeight: 400
              }}
            >
              {message.content}
            </Typography>
            
            {isEmail && (
              <Card 
                sx={{ 
                  mt: 2, 
                  backgroundColor: isUser ? 'rgba(255,255,255,0.1)' : '#f8f9fa',
                  border: isUser ? '1px solid rgba(255,255,255,0.2)' : '1px solid #e0e0e0',
                  borderRadius: '12px'
                }}
              >
                <CardContent sx={{ p: 2.5 }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
                    <EmailIcon 
                      sx={{ 
                        mr: 1, 
                        color: isUser ? '#ffffff' : '#4285f4',
                        fontSize: '1.2rem'
                      }} 
                    />
                    <Typography 
                      variant="subtitle2" 
                      sx={{ 
                        color: isUser ? '#ffffff' : '#4285f4',
                        fontWeight: 500,
                        fontSize: '0.875rem'
                      }}
                    >
                      Email Draft Ready
                    </Typography>
                  </Box>
                  
                  <Box sx={{ mb: 2 }}>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        mb: 1,
                        color: isUser ? 'rgba(255,255,255,0.9)' : '#5f6368',
                        fontSize: '0.8rem'
                      }}
                    >
                      <strong>To:</strong> {message.metadata.email_draft.recipient_email}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        mb: 1,
                        color: isUser ? 'rgba(255,255,255,0.9)' : '#5f6368',
                        fontSize: '0.8rem'
                      }}
                    >
                      <strong>Subject:</strong> {message.metadata.email_draft.subject}
                    </Typography>
                    <Typography 
                      variant="body2" 
                      sx={{ 
                        color: isUser ? 'rgba(255,255,255,0.9)' : '#202124',
                        fontSize: '0.85rem',
                        lineHeight: 1.4,
                        backgroundColor: isUser ? 'rgba(255,255,255,0.1)' : '#ffffff',
                        p: 1.5,
                        borderRadius: '8px',
                        border: isUser ? '1px solid rgba(255,255,255,0.2)' : '1px solid #e0e0e0'
                      }}
                    >
                      {message.metadata.email_draft.body}
                    </Typography>
                  </Box>
                  
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Button
                      variant={isUser ? "outlined" : "contained"}
                      size="small"
                      startIcon={<CheckIcon sx={{ fontSize: '1rem' }} />}
                      onClick={() => setEmailConfirmDialog(message.metadata.email_draft)}
                      sx={{
                        borderRadius: '20px',
                        textTransform: 'none',
                        fontWeight: 500,
                        fontSize: '0.8rem',
                        px: 2,
                        py: 0.5,
                        ...(isUser ? {
                          borderColor: 'rgba(255,255,255,0.5)',
                          color: '#ffffff',
                          '&:hover': {
                            borderColor: '#ffffff',
                            backgroundColor: 'rgba(255,255,255,0.1)'
                          }
                        } : {})
                      }}
                    >
                      Confirm & Send
                    </Button>
                    <Button
                      variant="outlined"
                      size="small"
                      startIcon={<EditIcon sx={{ fontSize: '1rem' }} />}
                      sx={{
                        borderRadius: '20px',
                        textTransform: 'none',
                        fontWeight: 500,
                        fontSize: '0.8rem',
                        px: 2,
                        py: 0.5,
                        borderColor: isUser ? 'rgba(255,255,255,0.5)' : '#dadce0',
                        color: isUser ? '#ffffff' : '#5f6368',
                        '&:hover': {
                          borderColor: isUser ? '#ffffff' : '#5f6368',
                          backgroundColor: isUser ? 'rgba(255,255,255,0.1)' : '#f8f9fa'
                        }
                      }}
                    >
                      Edit Draft
                    </Button>
                  </Box>
                </CardContent>
              </Card>
            )}
          </Paper>
          
          <Typography 
            variant="caption" 
            sx={{ 
              color: '#9aa0a6',
              fontSize: '0.75rem',
              mt: 0.5,
              ml: 1,
              display: 'block'
            }}
          >
            {new Date(message.timestamp).toLocaleTimeString([], { 
              hour: '2-digit', 
              minute: '2-digit' 
            })}
          </Typography>
        </Box>
        
        {isUser && (
          <Avatar 
            sx={{ 
              ml: 2, 
              width: 32, 
              height: 32,
              backgroundColor: userProfile?.profile_picture ? 'transparent' : '#34a853'
            }}
            src={userProfile?.profile_picture}
          >
            {!userProfile?.profile_picture && <PersonIcon sx={{ fontSize: '1.2rem' }} />}
          </Avatar>
        )}
      </Box>
    );
  };

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error" onClose={() => setError(null)}>
          {error}
        </Alert>
      </Box>
    );
  }

  return (
    <Box sx={{ 
      height: 'calc(100vh - 64px)', 
      display: 'flex', 
      flexDirection: 'column',
      backgroundColor: '#f8f9fa'
    }}>
      {/* Header */}
      <Paper 
        elevation={0} 
        sx={{ 
          p: 3, 
          borderRadius: 0,
          backgroundColor: '#ffffff',
          borderBottom: '1px solid #e0e0e0'
        }}
      >
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography 
              variant="h5" 
              sx={{ 
                display: 'flex', 
                alignItems: 'center',
                fontFamily: 'Google Sans, Roboto, sans-serif',
                fontWeight: 400,
                color: '#202124',
                mb: 0.5
              }}
            >
              <Avatar
                sx={{
                  mr: 2,
                  width: 40,
                  height: 40,
                  backgroundColor: '#4285f4'
                }}
              >
                <BotIcon sx={{ fontSize: '1.5rem' }} />
              </Avatar>
              InboxIQ Assistant
            </Typography>
            <Typography 
              variant="body2" 
              sx={{ 
                color: '#5f6368',
                ml: 7,
                fontSize: '0.9rem'
              }}
            >
              Your AI-powered email assistant • Ask me to draft emails or answer questions
            </Typography>
          </Box>
          
          {/* User Menu */}
          {userProfile && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
              <Typography variant="body2" color="text.secondary">
                {userProfile.name}
              </Typography>
              <IconButton
                onClick={(e) => setUserMenuAnchor(e.currentTarget)}
                size="small"
              >
                {userProfile.profile_picture ? (
                  <Avatar
                    src={userProfile.profile_picture}
                    sx={{ width: 32, height: 32 }}
                  />
                ) : (
                  <Avatar sx={{ width: 32, height: 32, bgcolor: 'primary.main' }}>
                    <PersonIcon />
                  </Avatar>
                )}
              </IconButton>
            </Box>
          )}
        </Box>
      </Paper>

      {/* User Menu */}
      <Menu
        anchorEl={userMenuAnchor}
        open={Boolean(userMenuAnchor)}
        onClose={() => setUserMenuAnchor(null)}
        anchorOrigin={{
          vertical: 'bottom',
          horizontal: 'right',
        }}
        transformOrigin={{
          vertical: 'top',
          horizontal: 'right',
        }}
      >
        <MenuItem onClick={() => {
          setUserMenuAnchor(null);
          setProfileSetupDialog(true);
          setProfileForm({
            username: userProfile?.name || '',
            display_name: userProfile?.name || '',
            profile_picture: userProfile?.profile_picture || ''
          });
        }}>
          <SettingsIcon sx={{ mr: 1 }} />
          Edit Profile
        </MenuItem>
        <Divider />
        <MenuItem onClick={() => {
          setUserMenuAnchor(null);
          handleLogout();
        }}>
          <LogoutIcon sx={{ mr: 1 }} />
          Logout
        </MenuItem>
      </Menu>

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          py: 2,
          backgroundColor: '#f8f9fa',
          position: 'relative'
        }}
      >
        {messages.length === 0 && !loading && (
          <Box
            sx={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              height: '100%',
              textAlign: 'center',
              px: 4
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
              <BotIcon sx={{ fontSize: '2.5rem' }} />
            </Avatar>
            <Typography
              variant="h5"
              sx={{
                color: '#202124',
                mb: 1,
                fontFamily: 'Google Sans, Roboto, sans-serif',
                fontWeight: 400
              }}
            >
              Hi! I'm your InboxIQ Assistant
            </Typography>
            <Typography
              variant="body1"
              sx={{
                color: '#5f6368',
                mb: 3,
                maxWidth: '500px'
              }}
            >
              I can help you draft professional emails, manage your contacts, and streamline your communication. 
              Try saying something like "Send an email to John about the meeting" to get started.
            </Typography>
          </Box>
        )}

        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {loading && (
          <Box sx={{ 
            display: 'flex', 
            justifyContent: 'flex-start', 
            px: 2,
            mb: 3,
            alignItems: 'flex-start'
          }}>
            <Avatar 
              sx={{ 
                mr: 2, 
                width: 32, 
                height: 32,
                backgroundColor: '#4285f4'
              }}
            >
              <BotIcon sx={{ fontSize: '1.2rem' }} />
            </Avatar>
            <Paper
              elevation={0}
              sx={{
                p: 2,
                backgroundColor: '#ffffff',
                border: '1px solid #e0e0e0',
                borderRadius: '20px 20px 20px 6px',
                position: 'relative',
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  bottom: 0,
                  left: -6,
                  width: 0,
                  height: 0,
                  borderLeft: '6px solid transparent',
                  borderRight: '6px solid #ffffff',
                  borderTop: '6px solid #ffffff',
                  borderBottom: '6px solid transparent',
                }
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box
                  sx={{
                    display: 'flex',
                    gap: 0.5,
                    '& > div': {
                      width: 8,
                      height: 8,
                      borderRadius: '50%',
                      backgroundColor: '#9aa0a6',
                      animation: 'googlePulse 1.4s ease-in-out infinite both',
                    },
                    '& > div:nth-of-type(1)': {
                      animationDelay: '-0.32s',
                    },
                    '& > div:nth-of-type(2)': {
                      animationDelay: '-0.16s',
                    },
                    '& > div:nth-of-type(3)': {
                      animationDelay: '0s',
                    },
                  }}
                >
                  <div />
                  <div />
                  <div />
                </Box>
                <Typography variant="body2" sx={{ color: '#5f6368', ml: 1 }}>
                  Thinking...
                </Typography>
              </Box>
            </Paper>
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Paper 
        elevation={0} 
        sx={{ 
          p: 3, 
          borderRadius: 0,
          backgroundColor: '#ffffff',
          borderTop: '1px solid #e0e0e0'
        }}
      >
        <Box sx={{ 
          display: 'flex', 
          gap: 2,
          alignItems: 'flex-end',
          maxWidth: '1200px',
          mx: 'auto'
        }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Message InboxIQ Assistant..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading || !sessionId}
            variant="outlined"
            sx={{
              '& .MuiOutlinedInput-root': {
                borderRadius: '24px',
                backgroundColor: '#f1f3f4',
                border: 'none',
                '& fieldset': {
                  border: 'none',
                },
                '&:hover': {
                  backgroundColor: '#e8eaed',
                },
                '&.Mui-focused': {
                  backgroundColor: '#ffffff',
                  boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
                  '& fieldset': {
                    border: '2px solid #4285f4',
                  },
                },
                '& .MuiInputBase-input': {
                  py: 1.5,
                  px: 2,
                  fontSize: '1rem',
                  '&::placeholder': {
                    color: '#9aa0a6',
                    opacity: 1,
                  },
                },
              },
            }}
          />
          <Button
            variant="contained"
            onClick={sendMessage}
            disabled={!inputMessage.trim() || loading || !sessionId}
            sx={{
              minWidth: '48px',
              width: '48px',
              height: '48px',
              borderRadius: '50%',
              p: 0,
              boxShadow: '0 1px 2px 0 rgba(60,64,67,0.3), 0 1px 3px 1px rgba(60,64,67,0.15)',
              '&:hover': {
                boxShadow: '0 1px 3px 0 rgba(60,64,67,0.3), 0 4px 8px 3px rgba(60,64,67,0.15)',
              },
              '&:disabled': {
                backgroundColor: '#f1f3f4',
                color: '#9aa0a6',
                boxShadow: 'none',
              }
            }}
          >
            <SendIcon sx={{ fontSize: '1.2rem' }} />
          </Button>
        </Box>
      </Paper>

      {/* Email Confirmation Dialog */}
      <Dialog
        open={!!emailConfirmDialog}
        onClose={() => setEmailConfirmDialog(null)}
        maxWidth="md"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <EmailIcon sx={{ mr: 1 }} />
            Confirm Email
          </Box>
        </DialogTitle>
        
        <DialogContent>
          {emailConfirmDialog && (
            <Box>
              <Typography variant="h6" gutterBottom>
                Send email to {emailConfirmDialog.contact.name}?
              </Typography>
              
              <Card variant="outlined" sx={{ mt: 2 }}>
                <CardContent>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>To:</strong> {emailConfirmDialog.contact.email}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Subject:</strong> {emailConfirmDialog.email_preview.subject}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 2 }}>
                    <strong>Message:</strong>
                  </Typography>
                  
                  <Paper variant="outlined" sx={{ p: 2, mt: 1, bgcolor: 'grey.50' }}>
                    <Typography
                      variant="body2"
                      sx={{ whiteSpace: 'pre-wrap' }}
                    >
                      {emailConfirmDialog.email_preview.body}
                    </Typography>
                  </Paper>
                </CardContent>
              </Card>
            </Box>
          )}
        </DialogContent>
        
        <DialogActions>
          <Button
            onClick={() => handleEmailAction('cancel')}
            color="secondary"
            startIcon={<CloseIcon />}
          >
            Cancel
          </Button>
          
          <Button
            onClick={() => handleEmailAction('edit')}
            color="primary"
            variant="outlined"
            startIcon={<EditIcon />}
          >
            Edit
          </Button>
          
          <Button
            onClick={() => handleEmailAction('send')}
            color="primary"
            variant="contained"
            startIcon={<CheckIcon />}
            disabled={loading}
          >
            {loading ? <CircularProgress size={20} /> : 'Send Email'}
          </Button>
        </DialogActions>
      </Dialog>

      {/* Profile Setup Dialog */}
      <Dialog
        open={profileSetupDialog}
        onClose={() => setProfileSetupDialog(false)}
        maxWidth="sm"
        fullWidth
      >
        <DialogTitle>
          <Box sx={{ display: 'flex', alignItems: 'center' }}>
            <AccountCircleIcon sx={{ mr: 1 }} />
            Setup Your Profile
          </Box>
        </DialogTitle>
        
        <DialogContent>
          <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
            Let's personalize your InboxIQ experience! Set up your display name and profile picture.
          </Typography>
          
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            <TextField
              label="Username"
              value={profileForm.username}
              onChange={(e) => setProfileForm(prev => ({ ...prev, username: e.target.value }))}
              fullWidth
              variant="outlined"
              helperText="This will be used for login and internal references"
            />
            
            <TextField
              label="Display Name"
              value={profileForm.display_name}
              onChange={(e) => setProfileForm(prev => ({ ...prev, display_name: e.target.value }))}
              fullWidth
              variant="outlined"
              helperText="This is how you'll appear in emails and the chat interface"
              placeholder="e.g., John Smith"
            />
            
            <TextField
              label="Profile Picture URL"
              value={profileForm.profile_picture}
              onChange={(e) => setProfileForm(prev => ({ ...prev, profile_picture: e.target.value }))}
              fullWidth
              variant="outlined"
              helperText="Enter a URL to your profile picture (optional)"
              placeholder="https://example.com/your-photo.jpg"
            />
            
            {profileForm.profile_picture && (
              <Box sx={{ display: 'flex', justifyContent: 'center', mt: 2 }}>
                <Avatar
                  src={profileForm.profile_picture}
                  sx={{ width: 80, height: 80 }}
                  onError={() => setProfileForm(prev => ({ ...prev, profile_picture: '' }))}
                />
              </Box>
            )}
          </Box>
        </DialogContent>
        
        <DialogActions>
          <Button
            onClick={() => setProfileSetupDialog(false)}
            color="secondary"
          >
            Skip for Now
          </Button>
          
          <Button
            onClick={handleProfileUpdate}
            color="primary"
            variant="contained"
            disabled={loading || !profileForm.display_name.trim()}
            startIcon={loading ? <CircularProgress size={20} /> : <CheckIcon />}
          >
            {loading ? 'Saving...' : 'Save Profile'}
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}