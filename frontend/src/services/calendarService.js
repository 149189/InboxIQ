// src/services/calendarService.js

const API_BASE_URL = 'http://localhost:8000/api/calendar';

class CalendarService {
  constructor() {
    this.sessionId = null;
  }

  /**
   * Start a new calendar session
   */
  async startSession() {
    try {
      const response = await fetch(`${API_BASE_URL}/start/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      this.sessionId = data.session_id;
      return data;
    } catch (error) {
      console.error('Error starting calendar session:', error);
      throw error;
    }
  }

  /**
   * Send a message in the calendar session
   */
  async sendMessage(message) {
    if (!this.sessionId) {
      await this.startSession();
    }

    try {
      const response = await fetch(`${API_BASE_URL}/send/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
        body: JSON.stringify({
          session_id: this.sessionId,
          message: message,
        }),
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error sending calendar message:', error);
      throw error;
    }
  }

  /**
   * Get calendar chat history
   */
  async getHistory() {
    if (!this.sessionId) {
      return { messages: [] };
    }

    try {
      const response = await fetch(`${API_BASE_URL}/history/${this.sessionId}/`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data;
    } catch (error) {
      console.error('Error getting calendar history:', error);
      throw error;
    }
  }

  /**
   * Reset the session
   */
  resetSession() {
    this.sessionId = null;
  }

  /**
   * Check if session is active
   */
  hasActiveSession() {
    return this.sessionId !== null;
  }

  /**
   * Get current session ID
   */
  getSessionId() {
    return this.sessionId;
  }
}

// Create and export a singleton instance
const calendarService = new CalendarService();
export default calendarService;
