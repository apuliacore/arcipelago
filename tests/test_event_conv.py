import pytest
import datetime
from telegram.ext import ConversationHandler
from mockups import MockUpdate, MockMessage, MockContext, MockUser
from test_db import get_dummy_event
from arcipelago.event import Event
from arcipelago.conversations.create_event import (ask_poster, ask_event_name, ask_event_venue, ask_start_date,
	ask_start_time, ask_add_end_date, route_same_event, ask_end_date, ask_end_time_path_end_date, ask_category_path_end_time,
	ask_description,  ask_publication_date, ask_confirm_submission, process_submitted_event)
from arcipelago.conversations.create_event import (ASK_NAME, ASK_VENUE, ASK_EVENT_TYPE, ASK_START_DATE,
	ASK_START_TIME, ASK_ADD_END_DATE, ROUTE_SAME_EVENT, ASK_END_DATE, ASK_END_TIME_PATH_END_DATE,
	ASK_CATEGORY_PATH_END_TIME, ASK_DESCRIPTION, ASK_PUBLICATION_DATE, ASK_CONFIRM_SUBMISSION,
	PROCESS_EVENT)
from arcipelago.config import chatbot_token, authorized_users


def test_ask_poster():
	# evento gets executed when the command /evento
	# is sent to the bot. There's no special edge-case to test
	update = MockUpdate(MockMessage())
	context = MockContext()
	assert ask_poster(update, context) == ASK_NAME


def test_ask_event_name():
	update = MockUpdate(MockMessage())
	context = MockContext()
	assert ask_event_name(update, context) == ASK_VENUE


def test_ask_event_venue():
	update = MockUpdate(MockMessage('nome evento'))
	context = MockContext()
	assert ask_event_venue(update, context) == ASK_EVENT_TYPE


def test_ask_start_date():
	update = MockUpdate(MockMessage('Mostra'))
	context = MockContext()
	assert ask_start_date(update, context) == ASK_START_DATE

	update = MockUpdate(MockMessage('Evento singolo'))
	assert ask_start_date(update, context) == ASK_START_TIME


def test_ask_start_time():
	# wrong format
	update = MockUpdate(MockMessage('1/1/2023'))
	context = MockContext()
	assert ask_start_time(update, context) == ASK_START_TIME

	# past date
	past_date = (datetime.datetime.now().date() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
	update = MockUpdate(MockMessage(past_date))
	context = MockContext()
	assert ask_start_time(update, context) == ASK_START_TIME

	start_date = datetime.datetime.now().date().strftime('%d.%m.%Y')
	update = MockUpdate(MockMessage(start_date))
	context = MockContext()
	assert ask_start_time(update, context) == ASK_ADD_END_DATE


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
	now_plus_1h = (datetime.datetime.now() + datetime.timedelta(hours=1))
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
	assert route_same_event(update, context) == ASK_END_DATE


def test_ask_end_date():
	update = MockUpdate(MockMessage(''))
	context = MockContext()
	ask_end_date(update, context) == ASK_END_TIME_PATH_END_DATE


def test_ask_end_time_path_end_date():
	# wrong format
	update = MockUpdate(MockMessage('31/12/2022'))
	context = MockContext()
	assert ask_end_time_path_end_date(update, context) == ASK_END_TIME_PATH_END_DATE

	# wrong type
	update = MockUpdate(MockMessage('ciao'))
	assert ask_end_time_path_end_date(update, context) == ASK_END_TIME_PATH_END_DATE

	# wrong values
	update = MockUpdate(MockMessage('30.2.100'))
	assert ask_end_time_path_end_date(update, context) == ASK_END_TIME_PATH_END_DATE

	now_date = datetime.datetime.now().date().strftime('%d.%m.%Y')
	update = MockUpdate(MockMessage(now_date))
	assert ask_end_time_path_end_date(update, context) == ASK_CATEGORY_PATH_END_TIME


def test_ask_category_path_end_time():
	# Evento singolo
	dummy_event = Event()
	dummy_event.event_type = 'Evento singolo'
	dummy_event.start_datetime = datetime.datetime.now()

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
	now_datetime = datetime.datetime.now()
	dummy_event.start_datetime = now_datetime
	wrong_time = (now_datetime - datetime.timedelta(hours=1)).time()
	update = MockUpdate(MockMessage(wrong_time.strftime('%H:%M')))
	context = MockContext(dummy_event)
	assert ask_category_path_end_time(update, context) == ASK_CATEGORY_PATH_END_TIME

	# correct
	right_time = (now_datetime + datetime.timedelta(hours=1)).time()
	update = MockUpdate(MockMessage(right_time.strftime('%H:%M')))
	context = MockContext(dummy_event)
	assert ask_category_path_end_time(update, context) == ASK_DESCRIPTION


def test_ask_description():
	# non-existent category
	update = MockUpdate(MockMessage('concerti'))
	context = MockContext()

	assert ask_description(update, context) == ASK_DESCRIPTION

	update = MockUpdate(MockMessage('🎹 musica'))

	assert ask_description(update, context) == ASK_PUBLICATION_DATE


def test_ask_publication_date():
	# too long description
	update = MockUpdate(MockMessage('prova'*300))
	context = MockContext(get_dummy_event())
	assert ask_publication_date(update, context) == ASK_PUBLICATION_DATE

	update = MockUpdate(MockMessage('prova'))
	context = MockContext(get_dummy_event())
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

	now_date = datetime.datetime.now().date().strftime('%d.%m.%Y')
	update = MockUpdate(MockMessage(now_date))
	event = get_dummy_event()
	event.start_date = now_date
	context = MockContext(event)
	assert ask_confirm_submission(update, context) == PROCESS_EVENT


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
	try:
		process_submitted_event(mock_update, mock_context)
	except FileNotFoundError as err:
		assert 'locandine' in str(err)
