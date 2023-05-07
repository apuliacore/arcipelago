from google.oauth2 import service_account
from googleapiclient.discovery import build
import os
import datetime
from arcipelago.config import SERVICE_ACCOUNT_FILE, CALENDAR_ID


SCOPES = ["https://www.googleapis.com/auth/calendar"]


def build_service_obj():
   if SERVICE_ACCOUNT_FILE:
      credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
      return build('calendar', 'v3', credentials=credentials)
   else:
      return None


def add_event_to_gcalendar(event):
   service = build_service_obj()
   if service is not None:
      payload = {
           'summary': event.name,
           'location': event.venue,
           'description': event.description,
           'start': {
               'dateTime': event.start_datetime.strftime("%Y-%m-%dT%H:%M:00+01:00"),
               'timeZone': 'Europe/Rome',
           },
           'end': {
               'dateTime': event.end_datetime.strftime("%Y-%m-%dT%H:%M:00+01:00"),
               'timeZone': 'Europe/Rome',
           } if event.end_datetime is not None else
           {
               'dateTime': (event.start_datetime + datetime.timedelta(hours=2)).strftime("%Y-%m-%dT%H:%M:00+01:00"),
               'timeZone': 'Europe/Rome',
           }}

      # post event and get URL
      return service.events().insert(calendarId=CALENDAR_ID, body=payload).execute()
   else:
      pass


def delete_event_from_gcalendar(event_id):
   service = build_service_obj()
   if service is not None:
      payload = {
         "calendarId": CALENDAR_ID,
         "eventId": event_id,
      }
      return service.events().delete(**payload).execute()
   else:
      pass
