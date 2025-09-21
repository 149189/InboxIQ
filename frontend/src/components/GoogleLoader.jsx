// src/components/GoogleLoader.jsx
import React from 'react';
import { Box, CircularProgress } from '@mui/material';

const GoogleLoader = ({ size = 24, color = '#4285f4' }) => {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        '& .MuiCircularProgress-root': {
          color: color,
          animation: 'googleSpin 1s linear infinite',
        },
        '@keyframes googleSpin': {
          '0%': {
            transform: 'rotate(0deg)',
          },
          '100%': {
            transform: 'rotate(360deg)',
          },
        },
      }}
    >
      <CircularProgress size={size} thickness={3} />
    </Box>
  );
};

// Google-style typing indicator
export const TypingIndicator = () => {
  return (
    <Box
      sx={{
        display: 'flex',
        alignItems: 'center',
        gap: 0.5,
        p: 2,
      }}
    >
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
    </Box>
  );
};

export default GoogleLoader;
