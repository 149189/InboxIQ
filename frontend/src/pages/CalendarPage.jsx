// src/pages/CalendarPage.jsx
import React from 'react';
import {
  Box,
  Container,
  Typography,
  Paper,
  Grid,
  Card,
  CardContent,
  Avatar,
  Chip
} from '@mui/material';
import {
  CalendarToday as CalendarIcon,
  Event as EventIcon,
  Schedule as ScheduleIcon,
  AccessTime as TimeIcon,
  AutoAwesome as AIIcon
} from '@mui/icons-material';
import CalendarChat from '../components/CalendarChat';
import { CalendarProvider } from '../contexts/CalendarContext';

export default function CalendarPage() {
  const features = [
    {
      icon: <EventIcon sx={{ fontSize: 32, color: '#4285f4' }} />,
      title: 'Smart Event Creation',
      description: 'Create calendar events using natural language. Just tell me what you want to schedule.',
      color: '#4285f4'
    },
    {
      icon: <TimeIcon sx={{ fontSize: 32, color: '#34a853' }} />,
      title: 'Find Free Time',
      description: 'Ask me when you\'re available and I\'ll analyze your calendar to find the best time slots.',
      color: '#34a853'
    },
    {
      icon: <ScheduleIcon sx={{ fontSize: 32, color: '#fbbc04' }} />,
      title: 'Schedule Management',
      description: 'View upcoming events, reschedule meetings, and manage your calendar efficiently.',
      color: '#fbbc04'
    },
    {
      icon: <AIIcon sx={{ fontSize: 32, color: '#ea4335' }} />,
      title: 'AI-Powered Assistant',
      description: 'Powered by Gemini 2.5 Flash for intelligent calendar management and scheduling.',
      color: '#ea4335'
    }
  ];

  return (
    <CalendarProvider>
      <Box sx={{ minHeight: '100vh', bgcolor: '#f8f9fa' }}>
        {/* Header Section */}
        <Box
          sx={{
            bgcolor: 'linear-gradient(135deg, #4285f4 0%, #34a853 100%)',
            background: 'linear-gradient(135deg, #4285f4 0%, #34a853 100%)',
            color: 'white',
            py: 4
          }}
        >
          <Container maxWidth="xl">
            <Box sx={{ textAlign: 'center' }}>
              <Avatar
                sx={{
                  bgcolor: 'rgba(255,255,255,0.2)',
                  width: 64,
                  height: 64,
                  mx: 'auto',
                  mb: 2
                }}
              >
                <CalendarIcon sx={{ fontSize: 32 }} />
              </Avatar>
              
              <Typography
                variant="h3"
                component="h1"
                sx={{
                  fontWeight: 400,
                  mb: 1,
                  fontFamily: 'Google Sans, Roboto, sans-serif'
                }}
              >
                Calendar Assistant
              </Typography>
              
              <Typography
                variant="h6"
                sx={{
                  fontWeight: 400,
                  opacity: 0.9,
                  mb: 2
                }}
              >
                AI-powered calendar management for smarter scheduling
              </Typography>

              <Box sx={{ display: 'flex', justifyContent: 'center', gap: 1, flexWrap: 'wrap' }}>
                <Chip
                  label="✨ Powered by Gemini 2.5 Flash"
                  sx={{
                    bgcolor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    fontWeight: 500
                  }}
                />
                <Chip
                  label="🔗 Google Calendar Integration"
                  sx={{
                    bgcolor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    fontWeight: 500
                  }}
                />
                <Chip
                  label="🚀 Natural Language Processing"
                  sx={{
                    bgcolor: 'rgba(255,255,255,0.2)',
                    color: 'white',
                    fontWeight: 500
                  }}
                />
              </Box>
            </Box>
          </Container>
        </Box>

        <Container maxWidth="xl" sx={{ py: 4 }}>
          <Grid container spacing={4}>
            {/* Features Section */}
            <Grid item xs={12} lg={4}>
              <Typography
                variant="h5"
                sx={{
                  fontWeight: 500,
                  mb: 3,
                  color: '#202124',
                  fontFamily: 'Google Sans, Roboto, sans-serif'
                }}
              >
                What I Can Help You With
              </Typography>

              <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                {features.map((feature, index) => (
                  <Card
                    key={index}
                    elevation={0}
                    sx={{
                      border: '1px solid #e0e0e0',
                      borderRadius: 2,
                      transition: 'all 0.2s ease-in-out',
                      '&:hover': {
                        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
                        transform: 'translateY(-2px)'
                      }
                    }}
                  >
                    <CardContent sx={{ p: 3 }}>
                      <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                        <Avatar
                          sx={{
                            bgcolor: `${feature.color}15`,
                            width: 48,
                            height: 48,
                            mr: 2
                          }}
                        >
                          {feature.icon}
                        </Avatar>
                        <Box>
                          <Typography
                            variant="h6"
                            sx={{
                              fontWeight: 500,
                              color: '#202124',
                              mb: 1
                            }}
                          >
                            {feature.title}
                          </Typography>
                          <Typography
                            variant="body2"
                            sx={{
                              color: '#5f6368',
                              lineHeight: 1.5
                            }}
                          >
                            {feature.description}
                          </Typography>
                        </Box>
                      </Box>
                    </CardContent>
                  </Card>
                ))}
              </Box>

              {/* Example Prompts */}
              <Paper
                elevation={0}
                sx={{
                  mt: 3,
                  p: 3,
                  border: '1px solid #e0e0e0',
                  borderRadius: 2,
                  bgcolor: '#f8f9fa'
                }}
              >
                <Typography
                  variant="h6"
                  sx={{
                    fontWeight: 500,
                    mb: 2,
                    color: '#202124'
                  }}
                >
                  Try These Examples
                </Typography>
                
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 1 }}>
                  {[
                    "Schedule a team meeting for tomorrow at 2 PM",
                    "When am I free this week?",
                    "Show me my upcoming events",
                    "Create a recurring standup meeting every Monday",
                    "Find time for a 1-hour meeting with John next week"
                  ].map((example, index) => (
                    <Typography
                      key={index}
                      variant="body2"
                      sx={{
                        color: '#5f6368',
                        fontStyle: 'italic',
                        pl: 2,
                        borderLeft: '2px solid #dadce0'
                      }}
                    >
                      "{example}"
                    </Typography>
                  ))}
                </Box>
              </Paper>
            </Grid>

            {/* Chat Section */}
            <Grid item xs={12} lg={8}>
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
                <CalendarChat />
              </Paper>
            </Grid>
          </Grid>
        </Container>
      </Box>
    </CalendarProvider>
  );
}
