"""Test event related functions."""

from arcipelago.event import Event, check_events_collision
from arcipelago.db import insert_event, delete_event
import datetime


def test_start_date_setter():
	event = Event()

	# wrong format
	try:
		event.start_date = '13/12/2022'
	except Exception as e:
		assert 'gg.mm.aaaa' in str(e)

	# past date
	try:
		event.start_date = (datetime.datetime.now().date() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
	except Exception as e:
		assert 'passata' in str(e)

	# wrong type
	try:
		event.start_date = 13122022
	except Exception as e:
		assert 'type' in str(e)

	# correct assignment
	start_date = datetime.datetime.now().date()
	event.start_date = start_date.strftime('%d.%m.%Y')
	assert event.start_date == start_date


def test_start_time_setter():
	event = Event()
	event.start_date = datetime.datetime.now().date().strftime('%d.%m.%Y')

	# wrong format
	try:
		event.start_time = '21.00'
	except Exception as e:
		assert 'hh:mm' in str(e)

	# wrong values
	try:
		event.start_time = '24.00'
	except Exception as e:
		assert 'valido' in str(e)

	# wrong type
	try:
		event.start_time = 21
	except Exception as e:
		assert 'type' in str(e)

	# correct assignment
	now_plus_1h = (datetime.datetime.now() + datetime.timedelta(hours=1))
	start_time = now_plus_1h.time()
	event.start_date = now_plus_1h.date()
	event.start_time = start_time.strftime('%H:%M')
	assert event.start_time.strftime('%H:%M') == start_time.strftime('%H:%M')


def test_end_date_setter():
	event = Event()
	event.start_date = datetime.datetime.now().date().strftime('%d.%m.%Y')
	event.start_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).time().strftime('%H:%M')

	# wrong format
	try:
		event.end_date = '13/12/2022'
	except Exception as e:
		assert 'gg.mm.aaaa' in str(e)

	# end date before start date
	try:
		event.end_date = (event.start_date - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
	except Exception as e:
		assert 'precedente' in str(e)

	# wrong type
	try:
		event.end_date = 13122022
	except Exception as e:
		assert 'type' in str(e)

	# correct assignment
	end_date = event.start_date + datetime.timedelta(hours=2)
	event.end_date = end_date.strftime('%d.%m.%Y')
	assert event.end_date == end_date


def test_end_time_setter():
	event = Event()
	event.start_date = datetime.datetime.now().date().strftime('%d.%m.%Y')
	event.start_time = (datetime.datetime.now() + datetime.timedelta(minutes=1)).strftime('%H:%M')

	# wrong format
	try:
		event.end_time = '21.00'
	except Exception as e:
		assert 'hh:mm' in str(e)

	# wrong values
	try:
		event.end_time = '24.00'
	except Exception as e:
		assert 'valido' in str(e)

	# case without end date
	try:
		event.end_time = event.start_time.strftime('%H:%M')
	except Exception as e:
		assert 'precedente' in str(e)

	# case with end date equal to start date
	event.end_date = event.start_date
	try:
		event.end_time = event.start_time.strftime('%H:%M')
	except Exception as e:
		assert 'precedente' in str(e)

	# correct assignment
	now_plus_1h = (datetime.datetime.now() + datetime.timedelta(hours=1))
	end_time = now_plus_1h.time()
	event.end_date = now_plus_1h.date()
	event.end_time = end_time.strftime('%H:%M')
	assert event.end_time.strftime('%H:%M') == end_time.strftime('%H:%M')


def test_publication_date_setter():
	event = Event()
	event.start_date = (datetime.datetime.now().date() + datetime.timedelta(days=2)).strftime('%d.%m.%Y')

	# wrong format
	try:
		event.publication_date = '13/12/2022'
	except Exception as e:
		assert 'gg.mm.aaaa' in str(e)

	# past date
	try:
		event.publication_date = (datetime.datetime.now().date() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
	except Exception as e:
		assert 'passata' in str(e)

	# publication date after start date
	try:
		event.publication_date = (event.start_date + datetime.timedelta(days=1)).strftime('%d.%m.%Y')
	except Exception as e:
		assert 'successiva' in str(e)

	# wrong type
	try:
		event.publication_date = 13122022
	except Exception as e:
		assert 'type' in str(e)

	# correct assignment
	publication_date = event.start_date - datetime.timedelta(days=1)
	event.publication_date = publication_date.strftime('%d.%m.%Y')
	assert event.publication_date == publication_date


def test_check_events_collision():
	event = Event()
	event.name = "Nome"
	event.venue = "Venue"
	event.start_date = (datetime.datetime.now() + datetime.timedelta(days=2)).date().strftime('%d.%m.%Y')
	event.start_time = "21:00"

	# no future events
	colliding_event = check_events_collision(event)
	assert colliding_event is None

	# similar future event
	similar_event = Event()
	similar_event.name = "Name"
	similar_event.venue = event.venue
	similar_event.start_date = (datetime.datetime.now() + datetime.timedelta(days=1)).date().strftime('%d.%m.%Y')
	similar_event.start_time = event.start_time
	similar_event_id = insert_event(similar_event)
	colliding_event = check_events_collision(event)
	delete_event(similar_event_id)
	assert colliding_event is not None

	# different future event
	different_event = Event()
	different_event.name = "Evento"
	different_event.venue = "Locale"
	different_event.start_date = event.start_date
	different_event.start_time = event.start_time
	different_event_id = insert_event(different_event)
	colliding_event = check_events_collision(event)
	delete_event(different_event_id)
	assert colliding_event is None
