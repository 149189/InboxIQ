// src/services/promptDetectionService.js

/**
 * Service to detect whether a user prompt is related to Gmail or Calendar
 */
class PromptDetectionService {
  constructor() {
    // Calendar-related keywords and phrases
    this.calendarKeywords = [
      // Event creation
      'schedule', 'meeting', 'appointment', 'event', 'book', 'reserve',
      'plan', 'organize', 'arrange', 'set up', 'create event',
      
      // Time-related
      'calendar', 'date', 'time', 'when', 'tomorrow', 'today', 'next week',
      'next month', 'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
      'saturday', 'sunday', 'morning', 'afternoon', 'evening', 'night',
      'am', 'pm', 'o\'clock', 'hour', 'minute',
      
      // Calendar actions
      'free time', 'available', 'busy', 'conflict', 'reschedule', 'cancel',
      'postpone', 'move', 'change time', 'find time', 'check calendar',
      'my schedule', 'upcoming events', 'agenda', 'diary',
      
      // Meeting-specific
      'conference call', 'video call', 'zoom', 'teams', 'skype',
      'presentation', 'demo', 'review', 'standup', 'sync',
      'one-on-one', '1:1', 'all-hands', 'team meeting',
      
      // Reminders
      'remind', 'reminder', 'alert', 'notification', 'notify',
      
      // Recurring events
      'weekly', 'daily', 'monthly', 'recurring', 'repeat', 'every',
      
      // Location-related
      'room', 'conference room', 'office', 'location', 'venue', 'where'
    ];

    // Gmail-related keywords and phrases
    this.gmailKeywords = [
      // Email actions
      'email', 'mail', 'send', 'compose', 'draft', 'reply', 'forward',
      'message', 'letter', 'correspondence', 'communication',
      
      // Email management
      'inbox', 'sent', 'archive', 'delete', 'spam', 'trash',
      'folder', 'label', 'filter', 'search', 'find email',
      
      // Email composition
      'write', 'type', 'draft', 'compose', 'send to', 'email to',
      'cc', 'bcc', 'subject', 'attachment', 'attach',
      
      // Recipients
      'recipient', 'to', 'from', 'sender', 'receiver',
      
      // Email types
      'newsletter', 'notification', 'confirmation', 'invoice',
      'receipt', 'update', 'announcement', 'newsletter',
      
      // Email status
      'read', 'unread', 'important', 'starred', 'priority',
      'urgent', 'follow up', 'follow-up'
    ];

    // Phrases that strongly indicate calendar
    this.strongCalendarPhrases = [
      'schedule a meeting', 'book an appointment', 'create event',
      'check my calendar', 'find free time', 'when am i free',
      'upcoming events', 'my schedule', 'calendar invite',
      'meeting request', 'block time', 'time slot'
    ];

    // Phrases that strongly indicate Gmail
    this.strongGmailPhrases = [
      'send an email', 'compose email', 'draft email', 'email draft',
      'write email', 'send message', 'reply to email', 'forward email',
      'check inbox', 'email someone', 'send to'
    ];
  }

  /**
   * Detect if a prompt is calendar or Gmail related
   * @param {string} prompt - User input prompt
   * @returns {Object} - Detection result with type and confidence
   */
  detectPromptType(prompt) {
    if (!prompt || typeof prompt !== 'string') {
      return {
        type: 'unknown',
        confidence: 0,
        reasoning: 'Invalid or empty prompt'
      };
    }

    const normalizedPrompt = prompt.toLowerCase().trim();
    
    // Check for strong phrases first
    const strongCalendarMatch = this.strongCalendarPhrases.some(phrase => 
      normalizedPrompt.includes(phrase.toLowerCase())
    );
    
    const strongGmailMatch = this.strongGmailPhrases.some(phrase => 
      normalizedPrompt.includes(phrase.toLowerCase())
    );

    if (strongCalendarMatch && !strongGmailMatch) {
      return {
        type: 'calendar',
        confidence: 0.95,
        reasoning: 'Strong calendar phrase detected'
      };
    }

    if (strongGmailMatch && !strongCalendarMatch) {
      return {
        type: 'gmail',
        confidence: 0.95,
        reasoning: 'Strong Gmail phrase detected'
      };
    }

    // Count keyword matches
    const calendarMatches = this.countKeywordMatches(normalizedPrompt, this.calendarKeywords);
    const gmailMatches = this.countKeywordMatches(normalizedPrompt, this.gmailKeywords);

    // Calculate scores
    const totalMatches = calendarMatches + gmailMatches;
    
    if (totalMatches === 0) {
      return {
        type: 'unknown',
        confidence: 0,
        reasoning: 'No relevant keywords found'
      };
    }

    const calendarScore = calendarMatches / totalMatches;
    const gmailScore = gmailMatches / totalMatches;

    // Determine type based on scores
    if (calendarScore > gmailScore) {
      return {
        type: 'calendar',
        confidence: Math.min(calendarScore * 0.8, 0.9), // Cap at 0.9 for keyword-based detection
        reasoning: `Calendar keywords: ${calendarMatches}, Gmail keywords: ${gmailMatches}`
      };
    } else if (gmailScore > calendarScore) {
      return {
        type: 'gmail',
        confidence: Math.min(gmailScore * 0.8, 0.9),
        reasoning: `Gmail keywords: ${gmailMatches}, Calendar keywords: ${calendarMatches}`
      };
    } else {
      // Equal scores - look for context clues
      if (this.hasTimeContext(normalizedPrompt)) {
        return {
          type: 'calendar',
          confidence: 0.6,
          reasoning: 'Equal keyword matches but time context suggests calendar'
        };
      } else if (this.hasEmailContext(normalizedPrompt)) {
        return {
          type: 'gmail',
          confidence: 0.6,
          reasoning: 'Equal keyword matches but email context suggests Gmail'
        };
      } else {
        return {
          type: 'unknown',
          confidence: 0.3,
          reasoning: 'Equal keyword matches with no clear context'
        };
      }
    }
  }

  /**
   * Count how many keywords from a list appear in the prompt
   */
  countKeywordMatches(prompt, keywords) {
    return keywords.reduce((count, keyword) => {
      return count + (prompt.includes(keyword.toLowerCase()) ? 1 : 0);
    }, 0);
  }

  /**
   * Check if prompt has time-related context
   */
  hasTimeContext(prompt) {
    const timeIndicators = [
      'at', 'on', 'in', 'during', 'before', 'after',
      ':', 'am', 'pm', 'morning', 'afternoon', 'evening',
      'monday', 'tuesday', 'wednesday', 'thursday', 'friday',
      'saturday', 'sunday', 'tomorrow', 'today', 'next'
    ];
    
    return timeIndicators.some(indicator => prompt.includes(indicator));
  }

  /**
   * Check if prompt has email-related context
   */
  hasEmailContext(prompt) {
    const emailIndicators = [
      '@', '.com', '.org', '.net', 'subject:', 'dear', 'sincerely',
      'best regards', 'thank you', 'please', 'attachment'
    ];
    
    return emailIndicators.some(indicator => prompt.includes(indicator));
  }

  /**
   * Get suggestions for ambiguous prompts
   */
  getSuggestions(prompt) {
    const detection = this.detectPromptType(prompt);
    
    if (detection.confidence < 0.5) {
      return {
        suggestions: [
          "For calendar: Try 'Schedule a meeting for tomorrow at 2 PM'",
          "For email: Try 'Send an email to John about the project update'"
        ],
        needsClarification: true
      };
    }
    
    return {
      suggestions: [],
      needsClarification: false
    };
  }
}

// Create and export singleton instance
const promptDetectionService = new PromptDetectionService();
export default promptDetectionService;
