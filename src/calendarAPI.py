import json
from datetime import datetime, time, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from google.oauth2.credentials import Credentials


class EventNotFoundException(Exception):
    def __init__(self, message):
        self.message = message

def get_events(credentials, start_date, end_date):
    try:
        # Call the Calendar API
        credentials_data = json.loads(credentials)
        credentials = Credentials.from_authorized_user_info(credentials_data)
        
        service = build("calendar", "v3", credentials=credentials, cache_discovery=False)
        start = datetime.combine(start_date, time.min).replace(tzinfo=timezone.utc).isoformat() 
        end = datetime.combine(end_date, time.min).replace(tzinfo=timezone.utc).isoformat()
        
        events_query = service.events().list(
                calendarId="primary",
                timeMin=start,
                timeMax=end,
                maxResults=15,
                singleEvents=True,
                orderBy="startTime",
            ).execute()

        events_result = events_query.get("items", [])
        events = []

        if not events_result:
            events.append("No upcoming events found in the calendar.")
        else:
            for event in events_result:
                start = event['start'].get('dateTime', event['start'].get('date'))
                start_time = datetime.fromisoformat(start)
                event_time = start_time.strftime('%Y-%m-%d %H:%M')
                attendees = event.get('attendees', [])
                attendee_emails = [attendee['email'] for attendee in attendees]
                event_info = {
                    'id': event['id'],
                    'summary': event['summary'],
                    'time': event_time,
                    'attendes': attendee_emails
                }
                events.append(event_info)

    except HttpError as e:
        print(f"An error occurred: {e}")

    return events

def delete_event(credentials, event_id):
    try:
        # Delete the event
        calendar_service = build('calendar', 'v3', credentials=credentials)

        # Retrieve the event details
        event = calendar_service.events().get(calendarId='primary', eventId=event_id).execute()
        # Delete the event
        calendar_service.events().delete(calendarId='primary', eventId=event_id).execute()
        start = event['start'].get('dateTime', event['start'].get('date'))
        start_time = datetime.fromisoformat(start)
        event_time = start_time.strftime('%Y-%m-%d %H:%M')
        event_info = {
            'id': event['id'],
            'summary': event['summary'],
            'time': event_time
        }
        return event_info
    except HttpError as e:
        if e.status_code == 404:
            raise EventNotFoundException(f"Event with ID '{event_id}' not found in the calendar.")
        elif e.status_code == 410:
            raise EventNotFoundException(f"Event with ID '{event_id}' has already been deleted.")
        else:
            raise Exception(f"Error deleting event: {e}")
    except Exception as e:
        raise Exception(f"Error deleting event: {e}")


def create_event(credentials, summary, start_date, end_date, participants):
    # Create a Google Calendar API client
    calendar_service = build('calendar', 'v3', credentials=credentials)
    event = {
        'summary': summary,
        'start': {
            'dateTime': start_date.isoformat(),
            'timeZone': 'America/Los_Angeles',  # Pacific Time Zone
        },
        'end': {
            'dateTime': end_date.isoformat(),
            'timeZone': 'America/Los_Angeles',  # Pacific Time Zone
        },
        'attendees': [{'email': participant} for participant in participants],
    }
    

    try:
        event = calendar_service.events().insert(calendarId="primary", body=event, sendUpdates='all').execute()
    except Exception as e:
        print(f'An error occurred: {e}')
    return event


def update_event(credentials, event_id, summary, start_date, end_date, participants):
    try:
        # Call the Calendar API        
        service = build('calendar', 'v3', credentials=credentials)
        
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_date.isoformat(),
                'timeZone': 'America/Los_Angeles',  # Pacific Time Zone
            },
            'end': {
                'dateTime': end_date.isoformat(),
                'timeZone': 'America/Los_Angeles',  # Pacific Time Zone
            },
            'attendees': [{'email': participant} for participant in participants],
        }

        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event, sendUpdates='all').execute()
        return updated_event
    except HttpError as e:
        print(f"An error occurred: {e}")

    return None
