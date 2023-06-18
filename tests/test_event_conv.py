import pytest
import datetime
from telegram.ext import ConversationHandler
from mockups import MockUpdate, MockMessage, MockContext, MockUser
from test_db import get_dummy_event
from arcipelago.event import Event, Calendar
from arcipelago.conversations.create_event import (ask_poster, store_poster, store_event_name, ask_start_date,
	ask_start_time, ask_add_end_date, route_same_event, ask_end_date, store_end_date, store_opening_hours,
	store_event_venues_calendar, store_num_events, store_start_dates_calendar, store_start_times_calendar,
	store_events_duration_calendar, ask_end_time_path_end_date, ask_category_path_end_time, ask_description,
	ask_publication_date, ask_confirm_submission, process_submitted_event)
from arcipelago.conversations.create_event import (STORE_POSTER, STORE_EVENT_NAME, STORE_EVENT_TYPE,
	ASK_START_DATE, ASK_START_TIME, ASK_ADD_END_DATE, ROUTE_SAME_EVENT, ASK_END_DATE, ASK_END_TIME_PATH_END_DATE,
	STORE_END_DATE, STORE_OPENING_HOURS, STORE_NUM_EVENTS, STORE_EVENT_VENUES_CALENDAR, STORE_START_DATES_CALENDAR,
	STORE_START_TIMES_CALENDAR, STORE_EVENTS_DURATION_CALENDAR, ASK_CATEGORY_PATH_END_TIME, ASK_DESCRIPTION,
	ASK_PUBLICATION_DATE, ASK_CONFIRM_SUBMISSION, PROCESS_EVENT)
from arcipelago.config import chatbot_token, authorized_users


NOW = datetime.datetime.now()


def test_ask_poster():
	# evento gets executed when the command /evento
	# is sent to the bot. There's no special edge-case to test
	update = MockUpdate(MockMessage())
	context = MockContext()
	assert ask_poster(update, context) == STORE_POSTER


def test_store_poster():
	update = MockUpdate(MockMessage())
	context = MockContext()
	assert store_poster(update, context) == STORE_EVENT_NAME


def test_store_event_venues_calendar():
	num_events = 4
	dummy_calendar = Calendar()
	dummy_calendar.events = [Event() for _ in range(num_events)]
	context = MockContext()
	context.user_data['event'] = dummy_calendar

	## multiple values
	# wrong number of values
	update = MockUpdate(MockMessage('Luogo 1, Luogo 2'))
	assert store_event_venues_calendar(update, context) == STORE_EVENT_VENUES_CALENDAR

	# right values
	update = MockUpdate(MockMessage('Luogo 1, Luogo 2, Luogo 3, Luogo 4'))
	assert store_event_venues_calendar(update, context) == STORE_START_DATES_CALENDAR

	## single value
	# right value
	update = MockUpdate(MockMessage('Luogo 1'))
	assert store_event_venues_calendar(update, context) == STORE_START_DATES_CALENDAR


def test_store_num_events():
	# wrong type
	context = MockContext()
	context.user_data['old_event'] = Event()
	context.user_data['old_event'].from_chat = 1
	update = MockUpdate(MockMessage('due'))
	assert store_num_events(update, context) == STORE_NUM_EVENTS

	# wrong value
	update = MockUpdate(MockMessage('1'))
	assert store_num_events(update, context) == STORE_NUM_EVENTS
	update = MockUpdate(MockMessage('21'))
	assert store_num_events(update, context) == STORE_NUM_EVENTS

	# right value
	update = MockUpdate(MockMessage('7'))
	assert store_num_events(update, context) == STORE_EVENT_VENUES_CALENDAR
	assert len(context.user_data['event'].events) == 7


def test_store_start_dates_calendar():
	num_events = 5
	dummy_calendar = Calendar()
	dummy_calendar.events = [Event() for _ in range(num_events)]
	context = MockContext()
	context.user_data['event'] = dummy_calendar

	## multiple values
	# wrong number of values
	update = MockUpdate(MockMessage('21.05.2023, 21.05.2023'))
	assert store_start_dates_calendar(update, context) == STORE_START_DATES_CALENDAR

	# only one wrong value
	update = MockUpdate(MockMessage('21/05/2023, 21.05.2023, 21.05.2023, 21.05.2023, 21.05.2023'))
	assert store_start_dates_calendar(update, context) == STORE_START_DATES_CALENDAR

	# all wrong values
	update = MockUpdate(MockMessage('21/05/2023, 21/05/2023, 21/05/2023, 21/05/2023, 21/05/2023'))
	assert store_start_dates_calendar(update, context) == STORE_START_DATES_CALENDAR

	# right values
	now = NOW.date().strftime('%d.%m.%Y')
	tomorrow_date = (NOW + datetime.timedelta(days=1)).date().strftime('%d.%m.%Y')
	update = MockUpdate(MockMessage(f'{now}, {now}, {tomorrow_date}, {tomorrow_date}, {tomorrow_date}'))
	assert store_start_dates_calendar(update, context) == STORE_START_TIMES_CALENDAR

	## single value
	# wrong value
	update = MockUpdate(MockMessage('21/05/2023'))
	assert store_start_dates_calendar(update, context) == STORE_START_DATES_CALENDAR

	# right value
	update = MockUpdate(MockMessage(now))
	assert store_start_dates_calendar(update, context) == STORE_START_TIMES_CALENDAR


def test_store_start_times_calendar():
	num_events = 4
	dummy_calendar = Calendar()
	dummy_calendar.events = [Event() for _ in range(num_events)]
	context = MockContext()

	def start_time_tests(context):
		## multiple values
		# wrong number of values
		update = MockUpdate(MockMessage('20:00, 10:00'))
		assert store_start_times_calendar(update, context) == STORE_START_TIMES_CALENDAR

		# only one wrong value
		update = MockUpdate(MockMessage('20:00, 20:00, 10:00, 10'))
		assert store_start_times_calendar(update, context) == STORE_START_TIMES_CALENDAR

		# all wrong values
		update = MockUpdate(MockMessage('20, 20, 10, 10'))
		assert store_start_times_calendar(update, context) == STORE_START_TIMES_CALENDAR

		# right values
		update = MockUpdate(MockMessage('20:00, 20:00, 10:00, 10:00'))
		assert store_start_times_calendar(update, context) == STORE_EVENTS_DURATION_CALENDAR

		## single value
		# wrong value
		update = MockUpdate(MockMessage('50'))
		assert store_start_times_calendar(update, context) == STORE_START_TIMES_CALENDAR

		# right value
		update = MockUpdate(MockMessage('20:00'))
		assert store_start_times_calendar(update, context) == STORE_EVENTS_DURATION_CALENDAR

	# single start date
	start_date = (NOW + datetime.timedelta(days=1)).date()
	for event in dummy_calendar.events:
		event.start_date = start_date
	context.user_data['event'] = dummy_calendar
	start_time_tests(context)

	# multiple start dates
	start_dates = [(NOW + datetime.timedelta(days=1)).date(),
				   (NOW + datetime.timedelta(days=1)).date(),
				   (NOW + datetime.timedelta(days=2)).date(),
				   (NOW + datetime.timedelta(days=2)).date()]
	for event, start_date in zip(dummy_calendar.events, start_dates):
		event.start_date = start_date
	context.user_data['event'] = dummy_calendar
	start_time_tests(context)


def test_store_events_duration_calendar():
	num_events = 3
	dummy_calendar = Calendar()
	dummy_calendar.events = [Event() for _ in range(num_events)]
	for event in dummy_calendar.events:
		event.start_date = NOW.date()
		event.start_time = NOW.time()
	context = MockContext()
	context.user_data['event'] = dummy_calendar

	## multiple values
	# wrong number of values
	update = MockUpdate(MockMessage('2, 3'))
	store_events_duration_calendar(update, context) == STORE_EVENTS_DURATION_CALENDAR

	# only one wrong value
	update = MockUpdate(MockMessage('uno, 2, 3'))
	store_events_duration_calendar(update, context) == STORE_EVENTS_DURATION_CALENDAR

	# all wrong values
	update = MockUpdate(MockMessage('uno, due, tre'))
	store_events_duration_calendar(update, context) == STORE_EVENTS_DURATION_CALENDAR

	# right values
	update = MockUpdate(MockMessage('1, 2, 3'))
	store_events_duration_calendar(update, context) == ASK_DESCRIPTION

	## single value
	# wrong value
	update = MockUpdate(MockMessage('uno'))
	store_events_duration_calendar(update, context) == STORE_EVENTS_DURATION_CALENDAR

	# right value
	update = MockUpdate(MockMessage('1'))
	store_events_duration_calendar(update, context) == ASK_DESCRIPTION


def test_store_event_name():
	update = MockUpdate(MockMessage('nome evento'))
	context = MockContext()
	assert store_event_name(update, context) == STORE_EVENT_TYPE


def test_ask_start_date():
	update = MockUpdate(MockMessage('Mostra'))
	context = MockContext()
	assert ask_start_date(update, context) == ASK_START_DATE

	update = MockUpdate(MockMessage('Evento singolo'))
	assert ask_start_date(update, context) == ASK_START_TIME


def test_ask_start_time():
	# wrong format
	update = MockUpdate(MockMessage('1/1/2023'))
	context = MockContext(event=Event())
	assert ask_start_time(update, context) == ASK_START_TIME

	# past date
	past_date = (NOW.date() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
	update = MockUpdate(MockMessage(past_date))
	context = MockContext(event=Event())
	assert ask_start_time(update, context) == ASK_START_TIME

	start_date = NOW.date().strftime('%d.%m.%Y')
	update = MockUpdate(MockMessage(start_date))
	mock_event = Event(_event_type='Evento singolo')
	context = MockContext(event=mock_event)
	assert ask_start_time(update, context) == ASK_ADD_END_DATE

	start_date = NOW.date().strftime('%d.%m.%Y')
	mock_event = Event(_event_type='Esposizione')
	update = MockUpdate(MockMessage(start_date))
	context = MockContext(event=mock_event)
	assert ask_start_time(update, context) == STORE_END_DATE


def test_ask_add_end_date():
	# wrong format
	update = MockUpdate(MockMessage('13.12'))
	context = MockContext()
	assert ask_add_end_date(update, context) == ASK_ADD_END_DATE

	# wrong values
	update = MockUpdate(MockMessage('25:66'))
	context = MockContext()
	assert ask_add_end_date(update, context) == ASK_ADD_END_DATE

	# colliding event
	# TODO: add test

	# Rassegna o esposizione
	now_plus_1h = (NOW + datetime.timedelta(hours=1))
	start_time = now_plus_1h.time().strftime('%H:%M')
	update = MockUpdate(MockMessage(start_time))
	dummy_event = Event()
	dummy_event.start_date = now_plus_1h.date()
	context = MockContext(dummy_event)
	assert ask_add_end_date(update, context) == ASK_END_DATE

	# Evento singolo
	dummy_event = Event()
	dummy_event.start_date = now_plus_1h.date()
	dummy_event.event_type = 'Evento singolo'
	context = MockContext(dummy_event)
	update = MockUpdate(MockMessage(start_time))
	assert ask_add_end_date(update, context) == ASK_CATEGORY_PATH_END_TIME


def test_route_same_event():
	update = MockUpdate(MockMessage('Sì'))
	context = MockContext()
	assert route_same_event(update, context) == ConversationHandler.END

	update = MockUpdate(MockMessage('No'))
	context = MockContext(event=Event(_event_type='Evento singolo'))
	assert route_same_event(update, context) == ASK_END_DATE

	update = MockUpdate(MockMessage('No'))
	context = MockContext(event=Event(_event_type='Esposizione'))
	assert route_same_event(update, context) == ASK_DESCRIPTION


def test_ask_end_date():
	update = MockUpdate(MockMessage(''))
	context = MockContext()
	ask_end_date(update, context) == ASK_END_TIME_PATH_END_DATE


def test_store_end_date():
	# wrong format
	update = MockUpdate(MockMessage('31/12/2022'))
	context = MockContext(event=Event())
	assert store_end_date(update, context) == STORE_END_DATE

	# wrong type
	update = MockUpdate(MockMessage('ciao'))
	assert store_end_date(update, context) == STORE_END_DATE

	# wrong values
	update = MockUpdate(MockMessage('30.2.100'))
	assert store_end_date(update, context) == STORE_END_DATE

	now_date = NOW.date()
	tomorrow_date = now_date + datetime.timedelta(days=1)
	update = MockUpdate(MockMessage(tomorrow_date.strftime('%d.%m.%Y')))
	context = MockContext(event=Event(_start_date=now_date, _event_type='Evento singolo'))
	assert store_end_date(update, context) == None
	context = MockContext(event=Event(_start_date=now_date, _event_type='Esposizione'))
	assert store_end_date(update, context) == STORE_OPENING_HOURS


def test_store_opening_hours():
	# wrong format
	update = MockUpdate(MockMessage('10:00, 20:00'))
	context = MockContext(event=Event())
	assert store_opening_hours(update, context) == STORE_OPENING_HOURS

	# wrong time format
	update = MockUpdate(MockMessage('10 - 20'))
	context = MockContext(event=Event())
	assert store_opening_hours(update, context) == STORE_OPENING_HOURS

	# wrong values
	update = MockUpdate(MockMessage('20:00 - 10:00'))
	now_date = NOW.date()
	tomorrow_date = now_date + datetime.timedelta(days=1)
	context = MockContext(event=Event(_event_type='Esposizione', _start_date=now_date, _end_date=tomorrow_date))
	assert store_opening_hours(update, context) == STORE_OPENING_HOURS

	# right values
	now_date = NOW.date()
	time_10am, time8pm = '10:00', '20:00'
	tomorrow = now_date + datetime.timedelta(days=1)
	ten_days_from_now = now_date + datetime.timedelta(days=10)
	update = MockUpdate(MockMessage(f'{time_10am} - {time8pm}'))
	context = MockContext(event=Event(_event_type='Esposizione', _start_date=tomorrow, _end_date=ten_days_from_now))
	assert store_opening_hours(update, context) == ASK_DESCRIPTION


def test_ask_end_time_path_end_date():
	# wrong format
	update = MockUpdate(MockMessage('31/12/2022'))
	context = MockContext(event=Event())
	assert ask_end_time_path_end_date(update, context) == ASK_END_TIME_PATH_END_DATE

	# wrong type
	update = MockUpdate(MockMessage('ciao'))
	assert ask_end_time_path_end_date(update, context) == ASK_END_TIME_PATH_END_DATE

	# wrong values
	update = MockUpdate(MockMessage('30.2.100'))
	assert ask_end_time_path_end_date(update, context) == ASK_END_TIME_PATH_END_DATE

	now_date = NOW.date()
	tomorrow_date = now_date + datetime.timedelta(days=1)
	update = MockUpdate(MockMessage(tomorrow_date.strftime('%d.%m.%Y')))
	context = MockContext(event=Event(_start_date=now_date))
	assert ask_end_time_path_end_date(update, context) == ASK_CATEGORY_PATH_END_TIME


def test_ask_category_path_end_time():
	# Evento singolo
	dummy_event = Event()
	dummy_event.event_type = 'Evento singolo'
	dummy_event.start_datetime = NOW

	# wrong format
	update = MockUpdate(MockMessage('2 ore'))
	context = MockContext(dummy_event)
	assert ask_category_path_end_time(update, context) == ASK_CATEGORY_PATH_END_TIME

	# wrong event duration
	update = MockUpdate(MockMessage('-1'))
	context = MockContext(dummy_event)
	assert ask_category_path_end_time(update, context) == ASK_CATEGORY_PATH_END_TIME

	update = MockUpdate(MockMessage('50'))
	context = MockContext(dummy_event)
	assert ask_category_path_end_time(update, context) == ASK_CATEGORY_PATH_END_TIME

	# right event duration
	update = MockUpdate(MockMessage('2'))
	context = MockContext(dummy_event)
	assert ask_category_path_end_time(update, context) == ASK_DESCRIPTION

	# Rassegna o esposizione
	# wrong format
	update = MockUpdate(MockMessage('aaa'))
	context = MockContext()
	assert ask_category_path_end_time(update, context) == ASK_CATEGORY_PATH_END_TIME

	# wrong values
	dummy_event = Event()
	now_datetime = NOW
	dummy_event.start_datetime = now_datetime
	wrong_time = (now_datetime - datetime.timedelta(hours=1)).time()
	update = MockUpdate(MockMessage(wrong_time.strftime('%H:%M')))
	context = MockContext(dummy_event)
	assert ask_category_path_end_time(update, context) == ASK_CATEGORY_PATH_END_TIME

	# correct
	right_datetime = (now_datetime + datetime.timedelta(hours=1))
	right_time = right_datetime.time()
	update = MockUpdate(MockMessage(right_time.strftime('%H:%M')))
	dummy_event.end_date = right_datetime.date()
	context = MockContext(dummy_event)
	assert ask_category_path_end_time(update, context) == ASK_DESCRIPTION


def test_ask_description():
	# non-existent category
	update = MockUpdate(MockMessage('concerti'))
	context = MockContext()
	assert ask_description(update, context) == ASK_DESCRIPTION

	update = MockUpdate(MockMessage('🎹 musica'))
	assert ask_description(update, context) == ASK_PUBLICATION_DATE

	# event is a calendar
	dummy_calendar = Calendar()
	dummy_calendar.events = [Event() for _ in range(3)]
	context = MockContext()
	context.user_data['event'] = dummy_calendar

	update = MockUpdate(MockMessage('concerti'))
	assert ask_description(update, context) == ASK_DESCRIPTION

	update = MockUpdate(MockMessage('🎹 musica'))
	assert ask_description(update, context) == ASK_PUBLICATION_DATE


def test_ask_publication_date():
	# test case event is a calendar
	dummy_calendar = Calendar()
	dummy_calendar.events = [Event() for _ in range(3)]
	for event in dummy_calendar.events:
		event.start_datetime = NOW + datetime.timedelta(days=1)
	mock_events = [get_dummy_event(), dummy_calendar]

	for event in mock_events:
		# too long description
		update = MockUpdate(MockMessage('prova'*300))
		context = MockContext(event)
		assert ask_publication_date(update, context) == ASK_PUBLICATION_DATE

		update = MockUpdate(MockMessage('prova'))
		context = MockContext(event)
		assert ask_publication_date(update, context) == ASK_CONFIRM_SUBMISSION


def test_ask_confirm_submission():
	# wrong format
	update = MockUpdate(MockMessage('31/12/2022'))
	context = MockContext()
	assert ask_confirm_submission(update, context) == ASK_CONFIRM_SUBMISSION

	# wrong type
	update = MockUpdate(MockMessage('ciao'))
	assert ask_confirm_submission(update, context) == ASK_CONFIRM_SUBMISSION

	# wrong values
	update = MockUpdate(MockMessage('30.2.100'))
	assert ask_confirm_submission(update, context) == ASK_CONFIRM_SUBMISSION

	# test case normal event
	now_date = NOW.date().strftime('%d.%m.%Y')
	update = MockUpdate(MockMessage(now_date))
	event = get_dummy_event()
	event.start_date = now_date

	# test case event is a calendar
	dummy_calendar = Calendar()
	dummy_calendar.events = [Event() for _ in range(3)]
	for event in dummy_calendar.events:
		event.start_datetime = NOW + datetime.timedelta(days=1)
	mock_events = [event, dummy_calendar]

	for event in mock_events:
		context = MockContext(event)
		assert ask_confirm_submission(update, context) == PROCESS_EVENT


@pytest.mark.skip(reason="no way of currently testing this")
def test_process_submitted_event():
	# authorized user
	authorized_user = MockUser()
	authorized_user.id = list(authorized_users.keys())[0]
	mock_message = MockMessage(user=authorized_user)
	mock_update = MockUpdate(mock_message)
	mock_context = MockContext(get_dummy_event())
	mock_context.user_data['locandina'] = 'AgACAgQAAxkBAAEgwjZkV6zRdksaF-b0hn8C8eGlhud1GgACGLsxG9f-wFKIXnZJofu37QEAAwIAA3MAAy8E'
	try:
		process_submitted_event(mock_update, mock_context)
	except FileNotFoundError as err:
		assert 'locandine' in str(err)

	# unauthorized user
	unauthorized_user = MockUser('pluto987', 'Pluto', 123456)
	mock_update.message.from_user = unauthorized_user
	assert process_submitted_event(mock_update, mock_context) == ConversationHandler.END
