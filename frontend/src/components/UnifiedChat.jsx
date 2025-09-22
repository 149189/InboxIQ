// src/components/UnifiedChat.jsx
import React, { useState, useRef, useEffect } from 'react';
import {
  Box,
  Paper,
  TextField,
  Button,
  Typography,
  Avatar,
  Chip,
  CircularProgress,
  Alert,
  Divider,
  IconButton,
  Tooltip,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  Switch,
  FormControlLabel
} from '@mui/material';
import {
  Send as SendIcon,
  Email as EmailIcon,
  CalendarToday as CalendarIcon,
  AutoAwesome as AIIcon,
  Settings as SettingsIcon,
  Help as HelpIcon,
  Refresh as RefreshIcon
} from '@mui/icons-material';
import promptDetectionService from '../services/promptDetectionService';

export default function UnifiedChat({ 
  onGmailMessage, 
  onCalendarMessage, 
  gmailMessages = [], 
  calendarMessages = [], 
  isLoading = false,
  error = null 
}) {
  const [message, setMessage] = useState('');
  const [currentMode, setCurrentMode] = useState('auto'); // 'auto', 'gmail', 'calendar'
  const [detectionResult, setDetectionResult] = useState(null);
  const [showSettings, setShowSettings] = useState(false);
  const [autoDetection, setAutoDetection] = useState(true);
  const [allMessages, setAllMessages] = useState([]);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Combine and sort messages from both services
  useEffect(() => {
    const combined = [
      ...gmailMessages.map(msg => ({ ...msg, source: 'gmail' })),
      ...calendarMessages.map(msg => ({ ...msg, source: 'calendar' }))
    ].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));
    
    setAllMessages(combined);
  }, [gmailMessages, calendarMessages]);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [allMessages]);

  // Analyze message as user types
  useEffect(() => {
    if (message.trim() && autoDetection && currentMode === 'auto') {
      const result = promptDetectionService.detectPromptType(message);
      setDetectionResult(result);
    } else {
      setDetectionResult(null);
    }
  }, [message, autoDetection, currentMode]);

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const messageToSend = message.trim();
    let targetService = currentMode;

    // Auto-detect if in auto mode
    if (currentMode === 'auto' && autoDetection) {
      const detection = promptDetectionService.detectPromptType(messageToSend);
      
      if (detection.confidence > 0.6) {
        targetService = detection.type;
      } else {
        // Show disambiguation dialog for low confidence
        setDetectionResult(detection);
        return;
      }
    }

    setMessage('');
    setDetectionResult(null);

    try {
      if (targetService === 'gmail') {
        await onGmailMessage(messageToSend);
      } else if (targetService === 'calendar') {
        await onCalendarMessage(messageToSend);
      } else {
        // Default to Gmail if uncertain
        await onGmailMessage(messageToSend);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }

    inputRef.current?.focus();
  };

  const handleServiceSelection = async (service) => {
    const messageToSend = message.trim();
    setMessage('');
    setDetectionResult(null);

    try {
      if (service === 'gmail') {
        await onGmailMessage(messageToSend);
      } else {
        await onCalendarMessage(messageToSend);
      }
    } catch (error) {
      console.error('Failed to send message:', error);
    }
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const getServiceIcon = (source) => {
    return source === 'gmail' ? <EmailIcon sx={{ fontSize: 18 }} /> : <CalendarIcon sx={{ fontSize: 18 }} />;
  };

  const getServiceColor = (source) => {
    return source === 'gmail' ? '#ea4335' : '#4285f4';
  };

  const renderMessage = (msg, index) => {
    const isUser = msg.type === 'user';
    const serviceColor = getServiceColor(msg.source);

    return (
      <Box
        key={msg.id || index}
        sx={{
          display: 'flex',
          justifyContent: isUser ? 'flex-end' : 'flex-start',
          mb: 2,
          alignItems: 'flex-start'
        }}
      >
        {!isUser && (
          <Avatar
            sx={{
              bgcolor: serviceColor,
              width: 32,
              height: 32,
              mr: 1,
              mt: 0.5
            }}
          >
            {getServiceIcon(msg.source)}
          </Avatar>
        )}
        
        <Box sx={{ maxWidth: '70%', minWidth: '100px' }}>
          <Paper
            elevation={1}
            sx={{
              p: 2,
              bgcolor: isUser ? '#1a73e8' : '#f8f9fa',
              color: isUser ? 'white' : '#202124',
              borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px'
            }}
          >
            <Typography
              variant="body1"
              sx={{
                whiteSpace: 'pre-wrap',
                wordBreak: 'break-word',
                lineHeight: 1.4
              }}
            >
              {msg.content}
            </Typography>
            
            {msg.metadata?.drafts && (
              <Box sx={{ mt: 1 }}>
                <Chip
                  icon={<EmailIcon />}
                  label={`${msg.metadata.drafts.length} Email Draft${msg.metadata.drafts.length > 1 ? 's' : ''}`}
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Box>
            )}
            
            {msg.metadata?.type === 'event_draft' && (
              <Box sx={{ mt: 1 }}>
                <Chip
                  icon={<CalendarIcon />}
                  label="Event Draft"
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Box>
            )}
          </Paper>
          
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 0.5 }}>
            <Typography
              variant="caption"
              sx={{
                color: '#5f6368',
                textAlign: isUser ? 'right' : 'left'
              }}
            >
              {formatTimestamp(msg.timestamp)}
            </Typography>
            {!isUser && (
              <Chip
                label={msg.source === 'gmail' ? 'Gmail' : 'Calendar'}
                size="small"
                sx={{
                  ml: 1,
                  height: 16,
                  fontSize: '0.6rem',
                  bgcolor: `${serviceColor}15`,
                  color: serviceColor
                }}
              />
            )}
          </Box>
        </Box>
        
        {isUser && (
          <Avatar
            sx={{
              bgcolor: '#34a853',
              width: 32,
              height: 32,
              ml: 1,
              mt: 0.5
            }}
          >
            U
          </Avatar>
        )}
      </Box>
    );
  };

  return (
    <Box
      sx={{
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
        bgcolor: '#ffffff'
      }}
    >
      {/* Header */}
      <Box
        sx={{
          p: 2,
          borderBottom: '1px solid #e0e0e0',
          bgcolor: '#f8f9fa',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <Box sx={{ display: 'flex', alignItems: 'center' }}>
          <AIIcon sx={{ color: '#4285f4', mr: 1 }} />
          <Typography variant="h6" sx={{ fontWeight: 500, color: '#202124' }}>
            InboxIQ Assistant
          </Typography>
          
          {currentMode !== 'auto' && (
            <Chip
              label={currentMode === 'gmail' ? 'Gmail Mode' : 'Calendar Mode'}
              size="small"
              sx={{
                ml: 2,
                bgcolor: currentMode === 'gmail' ? '#ea433515' : '#4285f415',
                color: currentMode === 'gmail' ? '#ea4335' : '#4285f4'
              }}
            />
          )}
        </Box>
        
        <Box>
          <Tooltip title="Settings">
            <IconButton onClick={() => setShowSettings(true)} size="small">
              <SettingsIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert severity="error" sx={{ m: 2, borderRadius: 2 }}>
          {error}
        </Alert>
      )}

      {/* Detection Result */}
      {detectionResult && detectionResult.confidence < 0.6 && (
        <Alert
          severity="info"
          sx={{ m: 2, borderRadius: 2 }}
          action={
            <Box>
              <Button
                size="small"
                onClick={() => handleServiceSelection('gmail')}
                sx={{ mr: 1 }}
              >
                Gmail
              </Button>
              <Button
                size="small"
                onClick={() => handleServiceSelection('calendar')}
              >
                Calendar
              </Button>
            </Box>
          }
        >
          I'm not sure if this is about email or calendar. Which would you like to use?
        </Alert>
      )}

      {/* Messages Area */}
      <Box
        sx={{
          flex: 1,
          overflow: 'auto',
          p: 2,
          bgcolor: '#ffffff'
        }}
      >
        {allMessages.length === 0 && !isLoading && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <AIIcon sx={{ fontSize: 48, color: '#dadce0', mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#5f6368', mb: 1 }}>
              InboxIQ Assistant Ready
            </Typography>
            <Typography variant="body2" sx={{ color: '#5f6368', mb: 3 }}>
              I can help you with both email and calendar tasks. Just tell me what you need!
            </Typography>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
              <Chip label="📧 Draft an email" />
              <Chip label="📅 Schedule a meeting" />
              <Chip label="🔍 Find free time" />
              <Chip label="📝 Create event" />
            </Box>
          </Box>
        )}

        {allMessages.map((msg, index) => renderMessage(msg, index))}
        
        <div ref={messagesEndRef} />
      </Box>

      <Divider />

      {/* Input Area */}
      <Box
        component="form"
        onSubmit={handleSendMessage}
        sx={{
          p: 2,
          bgcolor: '#f8f9fa',
          display: 'flex',
          alignItems: 'center',
          gap: 1
        }}
      >
        <TextField
          ref={inputRef}
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          placeholder="Ask me about emails, calendar, or anything else..."
          variant="outlined"
          fullWidth
          multiline
          maxRows={4}
          disabled={isLoading}
          sx={{
            '& .MuiOutlinedInput-root': {
              borderRadius: '24px',
              bgcolor: '#ffffff',
              '& fieldset': {
                borderColor: detectionResult?.type === 'gmail' ? '#ea4335' : 
                            detectionResult?.type === 'calendar' ? '#4285f4' : '#dadce0',
              },
            },
          }}
        />
        
        {detectionResult && detectionResult.confidence > 0.6 && (
          <Tooltip title={`Detected: ${detectionResult.type} (${Math.round(detectionResult.confidence * 100)}% confidence)`}>
            <Avatar
              sx={{
                bgcolor: detectionResult.type === 'gmail' ? '#ea4335' : '#4285f4',
                width: 32,
                height: 32
              }}
            >
              {detectionResult.type === 'gmail' ? <EmailIcon sx={{ fontSize: 16 }} /> : <CalendarIcon sx={{ fontSize: 16 }} />}
            </Avatar>
          </Tooltip>
        )}
        
        <Button
          type="submit"
          variant="contained"
          disabled={!message.trim() || isLoading}
          sx={{
            minWidth: 'auto',
            width: 48,
            height: 48,
            borderRadius: '50%',
            p: 0
          }}
        >
          {isLoading ? (
            <CircularProgress size={24} color="inherit" />
          ) : (
            <SendIcon />
          )}
        </Button>
      </Box>

      {/* Settings Dialog */}
      <Dialog open={showSettings} onClose={() => setShowSettings(false)}>
        <DialogTitle>Chat Settings</DialogTitle>
        <DialogContent>
          <FormControlLabel
            control={
              <Switch
                checked={autoDetection}
                onChange={(e) => setAutoDetection(e.target.checked)}
              />
            }
            label="Auto-detect Gmail vs Calendar"
          />
          <Typography variant="body2" sx={{ color: '#5f6368', mt: 1 }}>
            When enabled, I'll automatically determine whether your message is about email or calendar.
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setShowSettings(false)}>Close</Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
}
