import datetime
import telegram
from arcipelago.config import main_channel
from arcipelago.db import get_events_to_be_published_today, set_published, get_events_in_date, get_event_from_name
from arcipelago.event import Event
from arcipelago.extra.gcalendar import add_event_to_gcalendar


def get_next_hour_datetime(hour: int, minutes: int = 0):
    if hour in range(0, 24):
        now = datetime.datetime.now()
        now_time = now.time()
        if now_time.hour <= hour:
            return datetime.datetime(now.year, now.month, now.day, hour, minutes)
        else:
            next_day = now + datetime.timedelta(days=1)
            return datetime.datetime(next_day.year, next_day.month, next_day.day, hour, minutes)
    else:
        raise ValueError("Hour should be an integer value between 0 and 23.")


def daily_publication_callback(context):
    events_res = get_events_to_be_published_today()
    for event_res in events_res:
        event = Event()
        event.load_from_res(event_res)
        publish_event(context.bot, event)


def daily_events_callback(context):
    now = datetime.datetime.now()
    todays_events = [Event().load_from_res(e) for e in get_events_in_date(now)]
    if len(todays_events) > 0:
        context.bot.send_message(main_channel, "\n\n".join([f"Eventi di oggi {now.strftime('%d.%m.%Y')}"] + [event.html(short=True) for event in todays_events]),
                                  parse_mode=telegram.ParseMode.HTML)


def check_event_will_get_published(event):
    date_today = datetime.datetime.now().date()
    time_now = datetime.datetime.now().time()

    if event.publication_date != date_today:
        return True
    else:
        if time_now > datetime.time(10):
            return False
        else:
            return True


def publish_event(bot, event):
    bot.send_photo(chat_id=main_channel,
                    photo=open(f'locandine/{event.id}.jpg', 'rb'),
                    caption=event.html(),
                    parse_mode=telegram.ParseMode.HTML)
    if event.event_type != 'Rassegna':
        set_published(event.id)
        add_event_to_gcalendar(event)
    else:
        calendar = event
        for event in calendar.events:
            set_published(event.id)
            add_event_to_gcalendar(event)
