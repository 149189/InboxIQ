import { createTheme } from '@mui/material/styles';

// Google-inspired color palette
const googleColors = {
  // Primary Google Blue
  blue: {
    50: '#e8f0fe',
    100: '#d2e3fc',
    200: '#aecbfa',
    300: '#8ab4f8',
    400: '#669df6',
    500: '#4285f4', // Main Google Blue
    600: '#1a73e8',
    700: '#1967d2',
    800: '#185abc',
    900: '#174ea6',
  },
  // Google Red
  red: {
    50: '#fce8e6',
    100: '#fad2cf',
    200: '#f6aea9',
    300: '#f28b82',
    400: '#ee675c',
    500: '#ea4335', // Main Google Red
    600: '#d93025',
    700: '#c5221f',
    800: '#b31412',
    900: '#a50e0e',
  },
  // Google Yellow
  yellow: {
    50: '#fef7e0',
    100: '#feefc3',
    200: '#fde68a',
    300: '#fcd34d',
    400: '#fbbf24',
    500: '#fbbc04', // Main Google Yellow
    600: '#f9ab00',
    700: '#f29900',
    800: '#ea8600',
    900: '#e37400',
  },
  // Google Green
  green: {
    50: '#e6f4ea',
    100: '#ceead6',
    200: '#a8dab5',
    300: '#81c995',
    400: '#5bb974',
    500: '#34a853', // Main Google Green
    600: '#1e8e3e',
    700: '#188038',
    800: '#137333',
    900: '#0d652d',
  },
  // Neutral grays (Google's approach)
  gray: {
    50: '#fafafa',
    100: '#f5f5f5',
    200: '#eeeeee',
    300: '#e0e0e0',
    400: '#bdbdbd',
    500: '#9e9e9e',
    600: '#757575',
    700: '#616161',
    800: '#424242',
    900: '#212121',
  },
  // Google's surface colors
  surface: {
    primary: '#ffffff',
    secondary: '#f8f9fa',
    tertiary: '#f1f3f4',
    elevated: '#ffffff',
  }
};

// Google's typography system
const googleTypography = {
  fontFamily: [
    'Google Sans',
    'Roboto',
    '-apple-system',
    'BlinkMacSystemFont',
    '"Segoe UI"',
    '"Helvetica Neue"',
    'Arial',
    'sans-serif',
  ].join(','),
  h1: {
    fontSize: '2.125rem', // 34px
    fontWeight: 400,
    lineHeight: 1.2,
    letterSpacing: '0.00735em',
  },
  h2: {
    fontSize: '1.75rem', // 28px
    fontWeight: 400,
    lineHeight: 1.2,
    letterSpacing: '0.00714em',
  },
  h3: {
    fontSize: '1.5rem', // 24px
    fontWeight: 400,
    lineHeight: 1.167,
    letterSpacing: '0em',
  },
  h4: {
    fontSize: '1.25rem', // 20px
    fontWeight: 500,
    lineHeight: 1.235,
    letterSpacing: '0.00735em',
  },
  h5: {
    fontSize: '1.125rem', // 18px
    fontWeight: 500,
    lineHeight: 1.334,
    letterSpacing: '0em',
  },
  h6: {
    fontSize: '1rem', // 16px
    fontWeight: 500,
    lineHeight: 1.6,
    letterSpacing: '0.0075em',
  },
  subtitle1: {
    fontSize: '1rem',
    fontWeight: 400,
    lineHeight: 1.75,
    letterSpacing: '0.00938em',
  },
  subtitle2: {
    fontSize: '0.875rem',
    fontWeight: 500,
    lineHeight: 1.57,
    letterSpacing: '0.00714em',
  },
  body1: {
    fontSize: '1rem',
    fontWeight: 400,
    lineHeight: 1.5,
    letterSpacing: '0.00938em',
  },
  body2: {
    fontSize: '0.875rem',
    fontWeight: 400,
    lineHeight: 1.43,
    letterSpacing: '0.01071em',
  },
  button: {
    fontSize: '0.875rem',
    fontWeight: 500,
    lineHeight: 1.75,
    letterSpacing: '0.02857em',
    textTransform: 'none', // Google doesn't use all caps
  },
  caption: {
    fontSize: '0.75rem',
    fontWeight: 400,
    lineHeight: 1.66,
    letterSpacing: '0.03333em',
  },
  overline: {
    fontSize: '0.75rem',
    fontWeight: 400,
    lineHeight: 2.66,
    letterSpacing: '0.08333em',
    textTransform: 'uppercase',
  },
};

// Create the Google-inspired theme
const googleTheme = createTheme({
  palette: {
    mode: 'light',
    primary: {
      main: googleColors.blue[500],
      light: googleColors.blue[300],
      dark: googleColors.blue[700],
      contrastText: '#ffffff',
    },
    secondary: {
      main: googleColors.green[500],
      light: googleColors.green[300],
      dark: googleColors.green[700],
      contrastText: '#ffffff',
    },
    error: {
      main: googleColors.red[500],
      light: googleColors.red[300],
      dark: googleColors.red[700],
      contrastText: '#ffffff',
    },
    warning: {
      main: googleColors.yellow[500],
      light: googleColors.yellow[300],
      dark: googleColors.yellow[700],
      contrastText: '#000000',
    },
    info: {
      main: googleColors.blue[500],
      light: googleColors.blue[300],
      dark: googleColors.blue[700],
      contrastText: '#ffffff',
    },
    success: {
      main: googleColors.green[500],
      light: googleColors.green[300],
      dark: googleColors.green[700],
      contrastText: '#ffffff',
    },
    grey: googleColors.gray,
    background: {
      default: googleColors.surface.secondary,
      paper: googleColors.surface.primary,
    },
    text: {
      primary: googleColors.gray[900],
      secondary: googleColors.gray[700],
      disabled: googleColors.gray[500],
    },
    divider: googleColors.gray[200],
  },
  typography: googleTypography,
  shape: {
    borderRadius: 8, // Google's preferred border radius
  },
  shadows: [
    'none',
    '0px 1px 2px 0px rgba(60,64,67,0.3), 0px 1px 3px 1px rgba(60,64,67,0.15)',
    '0px 1px 2px 0px rgba(60,64,67,0.3), 0px 2px 6px 2px rgba(60,64,67,0.15)',
    '0px 1px 3px 0px rgba(60,64,67,0.3), 0px 4px 8px 3px rgba(60,64,67,0.15)',
    '0px 2px 3px 0px rgba(60,64,67,0.3), 0px 6px 10px 4px rgba(60,64,67,0.15)',
    '0px 4px 4px 0px rgba(60,64,67,0.3), 0px 8px 12px 6px rgba(60,64,67,0.15)',
    '0px 6px 6px 0px rgba(60,64,67,0.3), 0px 10px 14px 8px rgba(60,64,67,0.15)',
    '0px 8px 8px 0px rgba(60,64,67,0.3), 0px 12px 16px 10px rgba(60,64,67,0.15)',
    '0px 10px 10px 0px rgba(60,64,67,0.3), 0px 14px 18px 12px rgba(60,64,67,0.15)',
    '0px 12px 12px 0px rgba(60,64,67,0.3), 0px 16px 20px 14px rgba(60,64,67,0.15)',
    '0px 14px 14px 0px rgba(60,64,67,0.3), 0px 18px 22px 16px rgba(60,64,67,0.15)',
    '0px 16px 16px 0px rgba(60,64,67,0.3), 0px 20px 24px 18px rgba(60,64,67,0.15)',
    '0px 18px 18px 0px rgba(60,64,67,0.3), 0px 22px 26px 20px rgba(60,64,67,0.15)',
    '0px 20px 20px 0px rgba(60,64,67,0.3), 0px 24px 28px 22px rgba(60,64,67,0.15)',
    '0px 22px 22px 0px rgba(60,64,67,0.3), 0px 26px 30px 24px rgba(60,64,67,0.15)',
    '0px 24px 24px 0px rgba(60,64,67,0.3), 0px 28px 32px 26px rgba(60,64,67,0.15)',
    '0px 26px 26px 0px rgba(60,64,67,0.3), 0px 30px 34px 28px rgba(60,64,67,0.15)',
    '0px 28px 28px 0px rgba(60,64,67,0.3), 0px 32px 36px 30px rgba(60,64,67,0.15)',
    '0px 30px 30px 0px rgba(60,64,67,0.3), 0px 34px 38px 32px rgba(60,64,67,0.15)',
    '0px 32px 32px 0px rgba(60,64,67,0.3), 0px 36px 40px 34px rgba(60,64,67,0.15)',
    '0px 34px 34px 0px rgba(60,64,67,0.3), 0px 38px 42px 36px rgba(60,64,67,0.15)',
    '0px 36px 36px 0px rgba(60,64,67,0.3), 0px 40px 44px 38px rgba(60,64,67,0.15)',
    '0px 38px 38px 0px rgba(60,64,67,0.3), 0px 42px 46px 40px rgba(60,64,67,0.15)',
    '0px 40px 40px 0px rgba(60,64,67,0.3), 0px 44px 48px 42px rgba(60,64,67,0.15)',
    '0px 42px 42px 0px rgba(60,64,67,0.3), 0px 46px 50px 44px rgba(60,64,67,0.15)',
  ],
  components: {
    // Button component customization
    MuiButton: {
      styleOverrides: {
        root: {
          borderRadius: 24, // Google's pill-shaped buttons
          textTransform: 'none',
          fontWeight: 500,
          padding: '8px 24px',
          boxShadow: 'none',
          '&:hover': {
            boxShadow: '0px 1px 2px 0px rgba(60,64,67,0.3), 0px 1px 3px 1px rgba(60,64,67,0.15)',
          },
        },
        contained: {
          '&:hover': {
            boxShadow: '0px 1px 3px 0px rgba(60,64,67,0.3), 0px 4px 8px 3px rgba(60,64,67,0.15)',
          },
        },
        outlined: {
          borderColor: googleColors.gray[300],
          '&:hover': {
            borderColor: googleColors.gray[400],
            backgroundColor: googleColors.surface.secondary,
          },
        },
      },
    },
    // Card component customization
    MuiCard: {
      styleOverrides: {
        root: {
          borderRadius: 12,
          border: `1px solid ${googleColors.gray[200]}`,
          boxShadow: '0px 1px 2px 0px rgba(60,64,67,0.3), 0px 1px 3px 1px rgba(60,64,67,0.15)',
        },
      },
    },
    // Paper component customization
    MuiPaper: {
      styleOverrides: {
        root: {
          borderRadius: 12,
        },
        outlined: {
          border: `1px solid ${googleColors.gray[200]}`,
        },
      },
    },
    // AppBar component customization
    MuiAppBar: {
      styleOverrides: {
        root: {
          backgroundColor: googleColors.surface.primary,
          color: googleColors.gray[900],
          boxShadow: '0px 1px 2px 0px rgba(60,64,67,0.3), 0px 1px 3px 1px rgba(60,64,67,0.15)',
          borderBottom: `1px solid ${googleColors.gray[200]}`,
        },
      },
    },
    // TextField component customization
    MuiTextField: {
      styleOverrides: {
        root: {
          '& .MuiOutlinedInput-root': {
            borderRadius: 8,
            '& fieldset': {
              borderColor: googleColors.gray[300],
            },
            '&:hover fieldset': {
              borderColor: googleColors.gray[400],
            },
            '&.Mui-focused fieldset': {
              borderColor: googleColors.blue[500],
              borderWidth: 2,
            },
          },
        },
      },
    },
    // Chip component customization
    MuiChip: {
      styleOverrides: {
        root: {
          borderRadius: 16,
        },
      },
    },
  },
});

export default googleTheme;
export { googleColors };
