import datetime
import random
from notification import get_next_hour_datetime, check_event_will_get_published
from event import Event


def test_get_next_hour_datetime():
	try:
		dt = get_next_hour_datetime(25)
	except Exception as e:
		assert 'integer' in str(e)

	_8am = 8
	_8pm = 20
	now = datetime.datetime.now()
	next_day = now + datetime.timedelta(days=1)
	dt8am = get_next_hour_datetime(_8am)
	dt8pm = get_next_hour_datetime(_8pm)

	if now.hour < _8am:
		assert dt8am.strftime('%d.%m.%Y-%H:%M') == datetime.datetime(now.year, now.month, now.day, _8am, 0).strftime('%d.%m.%Y-%H:%M')
		assert dt8pm.strftime('%d.%m.%Y-%H:%M') == datetime.datetime(now.year, now.month, now.day, _8pm, 0).strftime('%d.%m.%Y-%H:%M')
	elif _8am < now.hour < _8pm:
		assert dt8am.strftime('%d.%m.%Y-%H:%M') == datetime.datetime(next_day.year, next_day.month, next_day.day, _8am, 0).strftime('%d.%m.%Y-%H:%M')
		assert dt8pm.strftime('%d.%m.%Y-%H:%M') == datetime.datetime(now.year, now.month, now.day, _8pm, 0).strftime('%d.%m.%Y-%H:%M')
	else:
		assert dt8am.strftime('%d.%m.%Y-%H:%M') == datetime.datetime(next_day.year, next_day.month, next_day.day, _8am, 0).strftime('%d.%m.%Y-%H:%M')
		assert dt8pm.strftime('%d.%m.%Y-%H:%M') == datetime.datetime(next_day.year, next_day.month, next_day.day, _pam, 0).strftime('%d.%m.%Y-%H:%M')


def test_check_event_will_get_published():
	event = Event()
	date_today = datetime.datetime.now().date()
	event.start_date = date_today + datetime.timedelta(days=1)

	# event is not today
	assert check_event_will_get_published(event) == True

	event.start_date = date_today
	time_now = datetime.datetime.now().time()

	if time_now > datetime.time(13):
		assert check_event_will_get_published(event) == False
	else:
		assert check_event_will_get_published(event) == True