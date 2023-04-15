from test_db import get_dummy_event
from arcipelago.extra.gcalendar import add_event_to_gcalendar, delete_event_from_gcalendar
from arcipelago.config import SERVICE_ACCOUNT_FILE, CALENDAR_ID


def test_add_event_to_gcalendar():
   event = get_dummy_event()
   res = add_event_to_gcalendar(event)
   if SERVICE_ACCOUNT_FILE:
      assert res["summary"] == event.name
      res = delete_event_from_gcalendar(res["id"])
      assert not res  # successful operation returns an empty string
   else:
      assert res is None
