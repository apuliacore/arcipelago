import datetime
from telegram.ext import ConversationHandler
from mockups import MockUpdate, MockMessage, MockContext
from event import Event
from conversations.create_event import (ask_poster, ask_event_name, ask_event_venue, ask_start_date,
	data_inizio, orario_inizio, route_same_event, data_fine, data_fine_2)
from conversations.create_event import (ASK_NAME, ASK_VENUE, ASK_START_DATE, 
	DATA_INIZIO, ORARIO_INIZIO, ROUTE_SAME_EVENT, DATA_FINE, DATA_FINE_2,
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
	assert ask_start_date(update, context) == DATA_INIZIO


def test_data_inizio():
	# wrong format
	update = MockUpdate(MockMessage('1/1/2023'))
	context = MockContext()
	assert data_inizio(update, context) == DATA_INIZIO

	# past date
	past_date = (datetime.datetime.now().date() - datetime.timedelta(days=1)).strftime('%d.%m.%Y')
	update = MockUpdate(MockMessage(past_date))
	context = MockContext()
	assert data_inizio(update, context) == DATA_INIZIO

	start_date = datetime.datetime.now().date().strftime('%d.%m.%Y')
	update = MockUpdate(MockMessage(start_date))
	context = MockContext()
	assert data_inizio(update, context) == ORARIO_INIZIO


def test_orario_inizio():
	# wrong format
	update = MockUpdate(MockMessage('13.12'))
	context = MockContext()
	assert orario_inizio(update, context) == ORARIO_INIZIO

	# wrong values
	update = MockUpdate(MockMessage('25:66'))
	context = MockContext()
	assert orario_inizio(update, context) == ORARIO_INIZIO

	# colliding event
	# TODO: add test

	start_time = (datetime.datetime.now() + datetime.timedelta(hours=1)).time().strftime('%H:%M')
	update = MockUpdate(MockMessage(start_time))
	context = MockContext()
	assert orario_inizio(update, context) == DATA_FINE


def test_route_same_event():
	update = MockUpdate(MockMessage('Sì'))
	context = MockContext()
	assert route_same_event(update, context) == ConversationHandler.END

	update = MockUpdate(MockMessage('No'))
	assert route_same_event(update, context) == DATA_FINE


def test_data_fine():
	update = MockUpdate(MockMessage(''))
	context = MockContext()
	data_fine(update, context) == DATA_FINE_2


def test_data_fine_2():
	# wrong format
	update = MockUpdate(MockMessage('31/12/2022'))
	context = MockContext()
	assert data_fine_2(update, context) == DATA_FINE_2

	# wrong type
	update = MockUpdate(MockMessage('ciao'))
	assert data_fine_2(update, context) == DATA_FINE_2

	# wrong values
	update = MockUpdate(MockMessage('30.2.100'))
	assert data_fine_2(update, context) == DATA_FINE_2
	
	update = MockUpdate(MockMessage('30.3.2023'))
	assert data_fine_2(update, context) == ORARIO_FINE_2
