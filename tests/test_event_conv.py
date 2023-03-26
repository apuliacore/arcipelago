import datetime
from telegram.ext import ConversationHandler
from mockups import MockUpdate, MockMessage, MockContext
from event import Event
from conversations.create_event import (ask_poster, ask_event_name, ask_event_venue, ask_start_date,
	ask_start_time, ask_add_end_date, route_same_event, ask_end_date, ask_end_time)
from conversations.create_event import (ASK_NAME, ASK_VENUE, ASK_START_DATE, 
	ASK_START_TIME, ASK_ADD_END_DATE, ROUTE_SAME_EVENT, ASK_END_DATE, ASK_END_TIME,
	ORARIO_FINE_2)


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
	assert ask_event_venue(update, context) == ASK_START_DATE


def test_ask_start_date():
	update = MockUpdate(MockMessage('nome venue'))
	context = MockContext()
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

	start_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).time().strftime('%H:%M')
	update = MockUpdate(MockMessage(start_time))
	context = MockContext()
	assert ask_add_end_date(update, context) == ASK_END_DATE


def test_route_same_event():
	update = MockUpdate(MockMessage('Sì'))
	context = MockContext()
	assert route_same_event(update, context) == ConversationHandler.END

	update = MockUpdate(MockMessage('No'))
	assert route_same_event(update, context) == ASK_END_DATE


def test_ask_end_date():
	update = MockUpdate(MockMessage(''))
	context = MockContext()
	ask_end_date(update, context) == ASK_END_TIME


def test_ask_end_time():
	# wrong format
	update = MockUpdate(MockMessage('31/12/2022'))
	context = MockContext()
	assert ask_end_time(update, context) == ASK_END_TIME

	# wrong type
	update = MockUpdate(MockMessage('ciao'))
	assert ask_end_time(update, context) == ASK_END_TIME

	# wrong values
	update = MockUpdate(MockMessage('30.2.100'))
	assert ask_end_time(update, context) == ASK_END_TIME
	
	update = MockUpdate(MockMessage('30.3.2023'))
	assert ask_end_time(update, context) == ORARIO_FINE_2
