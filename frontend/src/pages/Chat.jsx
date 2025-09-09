// src/pages/Chat.jsx
import React, { useState, useEffect, useRef } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Avatar,
  Chip,
  Card,
  CardContent,
  IconButton,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  CircularProgress,
  Alert,
  Menu,
  MenuItem,
  Divider
} from '@mui/material';
import {
  Send as SendIcon,
  Person as PersonIcon,
  SmartToy as BotIcon,
  Email as EmailIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  Edit as EditIcon,
  Settings as SettingsIcon,
  AccountCircle as AccountCircleIcon,
  Logout as LogoutIcon
} from '@mui/icons-material';
import { useNavigate } from 'react-router-dom';

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [sessionId, setSessionId] = useState(null);
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
      .replace(/\n/g, '<br />');
  };

  const MessageBubble = ({ message }) => {
    const isUser = message.type === 'user';
    
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
          alignItems: 'flex-start'
        }}
      >
        {!isUser && (
          <Avatar sx={{ mr: 1, bgcolor: 'primary.main' }}>
            <BotIcon />
          </Avatar>
        )}
        
        <Paper
          elevation={1}
          sx={{
            p: 2,
            maxWidth: '70%',
            bgcolor: isUser ? 'primary.main' : 'grey.100',
            color: isUser ? 'white' : 'text.primary',
            borderRadius: 2,
            position: 'relative'
          }}
        >
          <Typography
            variant="body1"
            dangerouslySetInnerHTML={{
              __html: formatMessage(message.content)
            }}
          />
          
          {message.metadata?.type === 'email_confirmation' && (
            <Box sx={{ mt: 2 }}>
              <Card variant="outlined" sx={{ bgcolor: 'background.paper' }}>
                <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                  <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                    <EmailIcon sx={{ mr: 1, color: 'primary.main' }} />
                    <Typography variant="subtitle2" color="primary">
                      Email Preview
                    </Typography>
                  </Box>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>To:</strong> {message.metadata.contact.name} ({message.metadata.contact.email})
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Subject:</strong> {message.metadata.email_preview.subject}
                  </Typography>
                  
                  <Typography variant="body2" color="text.secondary" sx={{ mt: 1 }}>
                    {message.metadata.email_preview.body.substring(0, 150)}...
                  </Typography>
                </CardContent>
              </Card>
            </Box>
          )}
          
          <Typography
            variant="caption"
            sx={{
              display: 'block',
              mt: 1,
              opacity: 0.7,
              fontSize: '0.75rem'
            }}
          >
            {new Date(message.timestamp).toLocaleTimeString()}
          </Typography>
        </Paper>
        
        {isUser && (
          <Avatar sx={{ ml: 1, bgcolor: 'secondary.main' }}>
            <PersonIcon />
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
    <Box sx={{ height: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header */}
      <Paper elevation={1} sx={{ p: 2, borderRadius: 0 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
          <Box>
            <Typography variant="h6" sx={{ display: 'flex', alignItems: 'center' }}>
              <BotIcon sx={{ mr: 1 }} />
              InboxIQ Assistant
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Ask me anything or say "send an email to [person]" to compose emails
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
          p: 2,
          bgcolor: 'grey.50'
        }}
      >
        {messages.map((message) => (
          <MessageBubble key={message.id} message={message} />
        ))}
        
        {loading && (
          <Box sx={{ display: 'flex', justifyContent: 'center', my: 2 }}>
            <CircularProgress size={24} />
          </Box>
        )}
        
        <div ref={messagesEndRef} />
      </Box>

      {/* Input Area */}
      <Paper elevation={3} sx={{ p: 2, borderRadius: 0 }}>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <TextField
            fullWidth
            multiline
            maxRows={4}
            placeholder="Type your message... (e.g., 'Send an email to John about the meeting')"
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyPress={handleKeyPress}
            disabled={loading || !sessionId}
            variant="outlined"
            size="small"
          />
          <Button
            variant="contained"
            onClick={sendMessage}
            disabled={!inputMessage.trim() || loading || !sessionId}
            sx={{ minWidth: 'auto', px: 2 }}
          >
            <SendIcon />
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