// src/contexts/CalendarContext.jsx
import React, { createContext, useContext, useReducer, useEffect } from 'react';
import calendarService from '../services/calendarService';

// Initial state
const initialState = {
  messages: [],
  sessionId: null,
  isLoading: false,
  error: null,
  isSessionActive: false,
};

// Action types
const ActionTypes = {
  SET_LOADING: 'SET_LOADING',
  SET_ERROR: 'SET_ERROR',
  SET_SESSION_ID: 'SET_SESSION_ID',
  ADD_MESSAGE: 'ADD_MESSAGE',
  SET_MESSAGES: 'SET_MESSAGES',
  RESET_SESSION: 'RESET_SESSION',
  SET_SESSION_ACTIVE: 'SET_SESSION_ACTIVE',
};

// Reducer
function calendarReducer(state, action) {
  switch (action.type) {
    case ActionTypes.SET_LOADING:
      return { ...state, isLoading: action.payload };
    
    case ActionTypes.SET_ERROR:
      return { ...state, error: action.payload, isLoading: false };
    
    case ActionTypes.SET_SESSION_ID:
      return { ...state, sessionId: action.payload, isSessionActive: true };
    
    case ActionTypes.ADD_MESSAGE:
      return { 
        ...state, 
        messages: [...state.messages, action.payload],
        isLoading: false,
        error: null
      };
    
    case ActionTypes.SET_MESSAGES:
      return { 
        ...state, 
        messages: action.payload,
        isLoading: false,
        error: null
      };
    
    case ActionTypes.RESET_SESSION:
      return {
        ...initialState,
        messages: []
      };
    
    case ActionTypes.SET_SESSION_ACTIVE:
      return { ...state, isSessionActive: action.payload };
    
    default:
      return state;
  }
}

// Create context
const CalendarContext = createContext();

// Provider component
export function CalendarProvider({ children }) {
  const [state, dispatch] = useReducer(calendarReducer, initialState);

  // Start a new calendar session
  const startSession = async () => {
    dispatch({ type: ActionTypes.SET_LOADING, payload: true });
    dispatch({ type: ActionTypes.SET_ERROR, payload: null });

    try {
      const response = await calendarService.startSession();
      
      dispatch({ type: ActionTypes.SET_SESSION_ID, payload: response.session_id });
      
      // Add welcome message
      if (response.message) {
        dispatch({ type: ActionTypes.ADD_MESSAGE, payload: {
          id: response.message.id,
          type: response.message.type,
          content: response.message.content,
          timestamp: response.message.timestamp,
          metadata: response.message.metadata || {}
        }});
      }
      
      return response;
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
      throw error;
    }
  };

  // Send a message
  const sendMessage = async (messageContent) => {
    dispatch({ type: ActionTypes.SET_LOADING, payload: true });
    dispatch({ type: ActionTypes.SET_ERROR, payload: null });

    try {
      // Add user message immediately
      const userMessage = {
        id: Date.now(),
        type: 'user',
        content: messageContent,
        timestamp: new Date().toISOString(),
        metadata: {}
      };
      dispatch({ type: ActionTypes.ADD_MESSAGE, payload: userMessage });

      // Send to backend
      const response = await calendarService.sendMessage(messageContent);
      
      // Add assistant response
      if (response.message) {
        dispatch({ type: ActionTypes.ADD_MESSAGE, payload: {
          id: response.message.id,
          type: response.message.type,
          content: response.message.content,
          timestamp: response.message.timestamp,
          metadata: response.message.metadata || {}
        }});
      }
      
      return response;
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
      
      // Add error message
      const errorMessage = {
        id: Date.now() + 1,
        type: 'assistant',
        content: `I'm sorry, I encountered an error: ${error.message}. Please try again.`,
        timestamp: new Date().toISOString(),
        metadata: { isError: true }
      };
      dispatch({ type: ActionTypes.ADD_MESSAGE, payload: errorMessage });
      
      throw error;
    }
  };

  // Load chat history
  const loadHistory = async () => {
    if (!state.sessionId) return;

    dispatch({ type: ActionTypes.SET_LOADING, payload: true });
    
    try {
      const response = await calendarService.getHistory();
      
      if (response.messages) {
        const formattedMessages = response.messages.map(msg => ({
          id: msg.id,
          type: msg.type,
          content: msg.content,
          timestamp: msg.timestamp,
          metadata: msg.metadata || {}
        }));
        
        dispatch({ type: ActionTypes.SET_MESSAGES, payload: formattedMessages });
      }
    } catch (error) {
      dispatch({ type: ActionTypes.SET_ERROR, payload: error.message });
    }
  };

  // Reset session
  const resetSession = () => {
    calendarService.resetSession();
    dispatch({ type: ActionTypes.RESET_SESSION });
  };

  // Check if session is active
  const checkSession = () => {
    const isActive = calendarService.hasActiveSession();
    dispatch({ type: ActionTypes.SET_SESSION_ACTIVE, payload: isActive });
    return isActive;
  };

  // Context value
  const value = {
    // State
    messages: state.messages,
    sessionId: state.sessionId,
    isLoading: state.isLoading,
    error: state.error,
    isSessionActive: state.isSessionActive,
    
    // Actions
    startSession,
    sendMessage,
    loadHistory,
    resetSession,
    checkSession,
  };

  return (
    <CalendarContext.Provider value={value}>
      {children}
    </CalendarContext.Provider>
  );
}

// Hook to use calendar context
export function useCalendar() {
  const context = useContext(CalendarContext);
  if (!context) {
    throw new Error('useCalendar must be used within a CalendarProvider');
  }
  return context;
}

export default CalendarContext;
