// src/components/CalendarChat.jsx
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
  Tooltip
} from '@mui/material';
import {
  Send as SendIcon,
  CalendarToday as CalendarIcon,
  Event as EventIcon,
  Schedule as ScheduleIcon,
  Refresh as RefreshIcon,
  Clear as ClearIcon
} from '@mui/icons-material';
import { useCalendar } from '../contexts/CalendarContext';

export default function CalendarChat() {
  const [message, setMessage] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const {
    messages,
    isLoading,
    error,
    isSessionActive,
    startSession,
    sendMessage,
    resetSession,
    loadHistory
  } = useCalendar();

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Start session on component mount
  useEffect(() => {
    if (!isSessionActive) {
      handleStartSession();
    }
  }, []);

  const handleStartSession = async () => {
    try {
      await startSession();
    } catch (error) {
      console.error('Failed to start calendar session:', error);
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!message.trim() || isLoading) return;

    const messageToSend = message.trim();
    setMessage('');
    setIsTyping(true);

    try {
      await sendMessage(messageToSend);
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsTyping(false);
      inputRef.current?.focus();
    }
  };

  const handleReset = () => {
    resetSession();
    handleStartSession();
  };

  const formatTimestamp = (timestamp) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
  };

  const renderMessage = (msg, index) => {
    const isUser = msg.type === 'user';
    const isError = msg.metadata?.isError;
    const isEventDraft = msg.metadata?.type === 'event_draft';

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
              bgcolor: isError ? '#ea4335' : '#4285f4',
              width: 32,
              height: 32,
              mr: 1,
              mt: 0.5
            }}
          >
            <CalendarIcon sx={{ fontSize: 18 }} />
          </Avatar>
        )}
        
        <Box
          sx={{
            maxWidth: '70%',
            minWidth: '100px'
          }}
        >
          <Paper
            elevation={1}
            sx={{
              p: 2,
              bgcolor: isUser ? '#1a73e8' : (isError ? '#fce8e6' : '#f8f9fa'),
              color: isUser ? 'white' : (isError ? '#d93025' : '#202124'),
              borderRadius: isUser ? '18px 18px 4px 18px' : '18px 18px 18px 4px',
              border: isError ? '1px solid #fce8e6' : 'none'
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
            
            {isEventDraft && (
              <Box sx={{ mt: 1 }}>
                <Chip
                  icon={<EventIcon />}
                  label="Event Draft"
                  size="small"
                  color="primary"
                  variant="outlined"
                />
              </Box>
            )}
          </Paper>
          
          <Typography
            variant="caption"
            sx={{
              color: '#5f6368',
              mt: 0.5,
              display: 'block',
              textAlign: isUser ? 'right' : 'left'
            }}
          >
            {formatTimestamp(msg.timestamp)}
          </Typography>
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

  const quickActions = [
    { label: 'Schedule Meeting', prompt: 'Schedule a team meeting for tomorrow at 2 PM' },
    { label: 'Find Free Time', prompt: 'When am I free this week?' },
    { label: 'Show Events', prompt: 'Show me my upcoming events' },
    { label: 'Create Event', prompt: 'Create a new calendar event' }
  ];

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
          <CalendarIcon sx={{ color: '#4285f4', mr: 1 }} />
          <Typography variant="h6" sx={{ fontWeight: 500, color: '#202124' }}>
            Calendar Assistant
          </Typography>
        </Box>
        
        <Box>
          <Tooltip title="Refresh Session">
            <IconButton onClick={loadHistory} size="small">
              <RefreshIcon />
            </IconButton>
          </Tooltip>
          <Tooltip title="Reset Chat">
            <IconButton onClick={handleReset} size="small">
              <ClearIcon />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {/* Error Alert */}
      {error && (
        <Alert 
          severity="error" 
          sx={{ m: 2, borderRadius: 2 }}
          onClose={() => {}}
        >
          {error}
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
        {messages.length === 0 && !isLoading && (
          <Box sx={{ textAlign: 'center', py: 4 }}>
            <CalendarIcon sx={{ fontSize: 48, color: '#dadce0', mb: 2 }} />
            <Typography variant="h6" sx={{ color: '#5f6368', mb: 1 }}>
              Calendar Assistant Ready
            </Typography>
            <Typography variant="body2" sx={{ color: '#5f6368', mb: 3 }}>
              I can help you schedule events, find free time, and manage your calendar.
            </Typography>
            
            {/* Quick Actions */}
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, justifyContent: 'center' }}>
              {quickActions.map((action, index) => (
                <Chip
                  key={index}
                  label={action.label}
                  onClick={() => setMessage(action.prompt)}
                  sx={{
                    cursor: 'pointer',
                    '&:hover': {
                      backgroundColor: '#e8f0fe'
                    }
                  }}
                />
              ))}
            </Box>
          </Box>
        )}

        {messages.map((msg, index) => renderMessage(msg, index))}
        
        {isTyping && (
          <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
            <Avatar sx={{ bgcolor: '#4285f4', width: 32, height: 32, mr: 1 }}>
              <CalendarIcon sx={{ fontSize: 18 }} />
            </Avatar>
            <Paper
              elevation={1}
              sx={{
                p: 2,
                bgcolor: '#f8f9fa',
                borderRadius: '18px 18px 18px 4px'
              }}
            >
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <CircularProgress size={16} sx={{ mr: 1 }} />
                <Typography variant="body2" sx={{ color: '#5f6368' }}>
                  Calendar Assistant is thinking...
                </Typography>
              </Box>
            </Paper>
          </Box>
        )}
        
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
          placeholder="Ask about your calendar, schedule events, or find free time..."
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
                borderColor: '#dadce0',
              },
              '&:hover fieldset': {
                borderColor: '#5f6368',
              },
              '&.Mui-focused fieldset': {
                borderColor: '#1a73e8',
              },
            },
          }}
        />
        
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
    </Box>
  );
}
