from data_models.event import Event
from data_models.timecube import Timecube

from datetime import timedelta
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from typing import List
import base64
import os
import pickle
import pytz


class GoogleCalendarService:
    SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']
    load_dotenv()

    def __init__(self):
        self.service = self._authenticate()

    def get_calendars(self):
        calendars_result = self.service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        return calendars

    def get_events_for_date(self, calendar_id: str, date_timecube: Timecube) -> List[Event]:
        # Confirm that the date_timecube has the expected timezone
        if date_timecube.local_tz != "America/New_York":
            raise ValueError(f"Expected timezone 'America/New_York', but got '{date_timecube.local_tz}'")

        # Localize to Eastern Time
        midnight_date = date_timecube.date_in_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        start_of_day = midnight_date.astimezone(pytz.utc).isoformat()  # Convert to UTC for API
        end_of_day = (midnight_date + timedelta(days=1)).astimezone(pytz.utc).isoformat()

        raw_events = self.service.events().list(
                calendarId=calendar_id,
                timeMin=start_of_day,
                timeMax=end_of_day,
                singleEvents=True,
                orderBy='startTime'
            ).execute()

        events_dtos = []
        if raw_events.get('items'):
            event: Event
            for item in raw_events.get('items'):
                event = Event.from_gcal_json(item)
                events_dtos.append(event)
        return events_dtos

    @staticmethod
    def _authenticate():
        token_bytes = base64.b64decode(os.environ['GOOGLE_OAUTH_TOKEN'])
        creds: Credentials = pickle.loads(token_bytes)

        # Refresh token if needed
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        return build("calendar", "v3", credentials=creds)
