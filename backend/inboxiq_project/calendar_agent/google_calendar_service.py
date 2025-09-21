# backend/inboxiq_project/calendar_agent/google_calendar_service.py

import json
import traceback
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from django.utils import timezone
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError


class GoogleCalendarServiceError(Exception):
    """Custom exception for Google Calendar API errors"""
    pass


class GoogleCalendarService:
    """Service for interacting with Google Calendar API"""
    
    def __init__(self, access_token: str):
        """
        Initialize the Google Calendar service
        
        Args:
            access_token: OAuth2 access token for Google Calendar API
        """
        self.access_token = access_token
        self.service = None
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the Google Calendar API service"""
        try:
            # Create credentials object
            credentials = Credentials(token=self.access_token)
            
            # Build the service
            self.service = build('calendar', 'v3', credentials=credentials)
            
        except Exception as e:
            raise GoogleCalendarServiceError(f"Failed to initialize Google Calendar service: {str(e)}")
    
    def list_calendars(self) -> List[Dict]:
        """
        List all calendars for the authenticated user
        
        Returns:
            List of calendar dictionaries
        """
        try:
            calendar_list = self.service.calendarList().list().execute()
            
            calendars = []
            for calendar_item in calendar_list.get('items', []):
                calendars.append({
                    'id': calendar_item['id'],
                    'summary': calendar_item.get('summary', ''),
                    'description': calendar_item.get('description', ''),
                    'primary': calendar_item.get('primary', False),
                    'access_role': calendar_item.get('accessRole', ''),
                    'background_color': calendar_item.get('backgroundColor', ''),
                    'foreground_color': calendar_item.get('foregroundColor', ''),
                })
            
            return calendars
            
        except HttpError as e:
            raise GoogleCalendarServiceError(f"Failed to list calendars: {str(e)}")
        except Exception as e:
            raise GoogleCalendarServiceError(f"Unexpected error listing calendars: {str(e)}")
    
    def get_primary_calendar_id(self) -> str:
        """
        Get the primary calendar ID for the user
        
        Returns:
            Primary calendar ID (usually the user's email)
        """
        try:
            calendars = self.list_calendars()
            
            for calendar in calendars:
                if calendar.get('primary', False):
                    return calendar['id']
            
            # Fallback to 'primary' if no primary calendar found
            return 'primary'
            
        except Exception as e:
            print(f"Error getting primary calendar ID: {e}")
            return 'primary'
    
    def create_event(self, 
                    title: str,
                    start_datetime: datetime,
                    end_datetime: datetime,
                    description: str = '',
                    location: str = '',
                    attendees: List[str] = None,
                    reminders: List[Dict] = None,
                    calendar_id: str = 'primary') -> Dict:
        """
        Create a new calendar event
        
        Args:
            title: Event title
            start_datetime: Event start time
            end_datetime: Event end time
            description: Event description
            location: Event location
            attendees: List of attendee email addresses
            reminders: List of reminder configurations
            calendar_id: Calendar ID to create event in
        
        Returns:
            Created event dictionary
        """
        try:
            # Prepare event data
            event_data = {
                'summary': title,
                'description': description,
                'location': location,
                'start': {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': str(start_datetime.tzinfo) if start_datetime.tzinfo else 'UTC',
                },
                'end': {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': str(end_datetime.tzinfo) if end_datetime.tzinfo else 'UTC',
                },
            }
            
            # Add attendees if provided
            if attendees:
                event_data['attendees'] = [{'email': email} for email in attendees]
            
            # Add reminders if provided
            if reminders:
                event_data['reminders'] = {
                    'useDefault': False,
                    'overrides': reminders
                }
            else:
                event_data['reminders'] = {'useDefault': True}
            
            # Create the event
            created_event = self.service.events().insert(
                calendarId=calendar_id,
                body=event_data
            ).execute()
            
            return self._format_event(created_event)
            
        except HttpError as e:
            raise GoogleCalendarServiceError(f"Failed to create event: {str(e)}")
        except Exception as e:
            raise GoogleCalendarServiceError(f"Unexpected error creating event: {str(e)}")
    
    def update_event(self,
                    event_id: str,
                    title: str = None,
                    start_datetime: datetime = None,
                    end_datetime: datetime = None,
                    description: str = None,
                    location: str = None,
                    attendees: List[str] = None,
                    calendar_id: str = 'primary') -> Dict:
        """
        Update an existing calendar event
        
        Args:
            event_id: Google Calendar event ID
            title: New event title
            start_datetime: New start time
            end_datetime: New end time
            description: New description
            location: New location
            attendees: New list of attendee emails
            calendar_id: Calendar ID containing the event
        
        Returns:
            Updated event dictionary
        """
        try:
            # Get existing event
            existing_event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            # Update fields if provided
            if title is not None:
                existing_event['summary'] = title
            
            if description is not None:
                existing_event['description'] = description
            
            if location is not None:
                existing_event['location'] = location
            
            if start_datetime is not None:
                existing_event['start'] = {
                    'dateTime': start_datetime.isoformat(),
                    'timeZone': str(start_datetime.tzinfo) if start_datetime.tzinfo else 'UTC',
                }
            
            if end_datetime is not None:
                existing_event['end'] = {
                    'dateTime': end_datetime.isoformat(),
                    'timeZone': str(end_datetime.tzinfo) if end_datetime.tzinfo else 'UTC',
                }
            
            if attendees is not None:
                existing_event['attendees'] = [{'email': email} for email in attendees]
            
            # Update the event
            updated_event = self.service.events().update(
                calendarId=calendar_id,
                eventId=event_id,
                body=existing_event
            ).execute()
            
            return self._format_event(updated_event)
            
        except HttpError as e:
            raise GoogleCalendarServiceError(f"Failed to update event: {str(e)}")
        except Exception as e:
            raise GoogleCalendarServiceError(f"Unexpected error updating event: {str(e)}")
    
    def delete_event(self, event_id: str, calendar_id: str = 'primary') -> bool:
        """
        Delete a calendar event
        
        Args:
            event_id: Google Calendar event ID
            calendar_id: Calendar ID containing the event
        
        Returns:
            True if successful
        """
        try:
            self.service.events().delete(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return True
            
        except HttpError as e:
            raise GoogleCalendarServiceError(f"Failed to delete event: {str(e)}")
        except Exception as e:
            raise GoogleCalendarServiceError(f"Unexpected error deleting event: {str(e)}")
    
    def get_events(self,
                  start_date: datetime = None,
                  end_date: datetime = None,
                  max_results: int = 50,
                  calendar_id: str = 'primary') -> List[Dict]:
        """
        Get events from calendar within a date range
        
        Args:
            start_date: Start date for event search
            end_date: End date for event search
            max_results: Maximum number of events to return
            calendar_id: Calendar ID to search
        
        Returns:
            List of event dictionaries
        """
        try:
            # Set default date range if not provided
            if start_date is None:
                start_date = timezone.now()
            
            if end_date is None:
                end_date = start_date + timedelta(days=30)
            
            # Get events
            events_result = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                maxResults=max_results,
                singleEvents=True,
                orderBy='startTime'
            ).execute()
            
            events = []
            for event in events_result.get('items', []):
                events.append(self._format_event(event))
            
            return events
            
        except HttpError as e:
            raise GoogleCalendarServiceError(f"Failed to get events: {str(e)}")
        except Exception as e:
            raise GoogleCalendarServiceError(f"Unexpected error getting events: {str(e)}")
    
    def get_event(self, event_id: str, calendar_id: str = 'primary') -> Dict:
        """
        Get a specific event by ID
        
        Args:
            event_id: Google Calendar event ID
            calendar_id: Calendar ID containing the event
        
        Returns:
            Event dictionary
        """
        try:
            event = self.service.events().get(
                calendarId=calendar_id,
                eventId=event_id
            ).execute()
            
            return self._format_event(event)
            
        except HttpError as e:
            raise GoogleCalendarServiceError(f"Failed to get event: {str(e)}")
        except Exception as e:
            raise GoogleCalendarServiceError(f"Unexpected error getting event: {str(e)}")
    
    def find_free_time(self,
                      duration_minutes: int,
                      start_date: datetime = None,
                      end_date: datetime = None,
                      calendar_id: str = 'primary') -> List[Dict]:
        """
        Find free time slots in the calendar
        
        Args:
            duration_minutes: Required duration in minutes
            start_date: Start date for search
            end_date: End date for search
            calendar_id: Calendar ID to search
        
        Returns:
            List of free time slot dictionaries
        """
        try:
            # Set default date range if not provided
            if start_date is None:
                start_date = timezone.now()
            
            if end_date is None:
                end_date = start_date + timedelta(days=7)
            
            # Get existing events
            events = self.get_events(start_date, end_date, calendar_id=calendar_id)
            
            # Find free slots (simplified algorithm)
            free_slots = []
            current_time = start_date
            
            # Sort events by start time
            events.sort(key=lambda x: x['start_datetime'])
            
            for event in events:
                event_start = datetime.fromisoformat(event['start_datetime'].replace('Z', '+00:00'))
                
                # Check if there's enough time before this event
                if (event_start - current_time).total_seconds() >= duration_minutes * 60:
                    free_slots.append({
                        'start_datetime': current_time.isoformat(),
                        'end_datetime': event_start.isoformat(),
                        'duration_minutes': int((event_start - current_time).total_seconds() / 60)
                    })
                
                # Move current time to after this event
                event_end = datetime.fromisoformat(event['end_datetime'].replace('Z', '+00:00'))
                current_time = max(current_time, event_end)
            
            # Check for free time after the last event
            if (end_date - current_time).total_seconds() >= duration_minutes * 60:
                free_slots.append({
                    'start_datetime': current_time.isoformat(),
                    'end_datetime': end_date.isoformat(),
                    'duration_minutes': int((end_date - current_time).total_seconds() / 60)
                })
            
            return free_slots
            
        except Exception as e:
            raise GoogleCalendarServiceError(f"Error finding free time: {str(e)}")
    
    def _format_event(self, google_event: Dict) -> Dict:
        """
        Format a Google Calendar event into our standard format
        
        Args:
            google_event: Raw Google Calendar event
        
        Returns:
            Formatted event dictionary
        """
        try:
            # Handle different date/time formats
            start_info = google_event.get('start', {})
            end_info = google_event.get('end', {})
            
            # Extract datetime or date
            if 'dateTime' in start_info:
                start_datetime = start_info['dateTime']
                end_datetime = end_info['dateTime']
                all_day = False
            else:
                start_datetime = start_info.get('date', '')
                end_datetime = end_info.get('date', '')
                all_day = True
            
            # Extract attendees
            attendees = []
            for attendee in google_event.get('attendees', []):
                attendees.append({
                    'email': attendee.get('email', ''),
                    'name': attendee.get('displayName', ''),
                    'response_status': attendee.get('responseStatus', 'needsAction'),
                    'optional': attendee.get('optional', False)
                })
            
            return {
                'id': google_event.get('id', ''),
                'title': google_event.get('summary', ''),
                'description': google_event.get('description', ''),
                'location': google_event.get('location', ''),
                'start_datetime': start_datetime,
                'end_datetime': end_datetime,
                'all_day': all_day,
                'status': google_event.get('status', 'confirmed'),
                'attendees': attendees,
                'creator': google_event.get('creator', {}),
                'organizer': google_event.get('organizer', {}),
                'html_link': google_event.get('htmlLink', ''),
                'created': google_event.get('created', ''),
                'updated': google_event.get('updated', ''),
            }
            
        except Exception as e:
            print(f"Error formatting event: {e}")
            return {
                'id': google_event.get('id', ''),
                'title': google_event.get('summary', 'Untitled Event'),
                'error': f"Failed to format event: {str(e)}"
            }
