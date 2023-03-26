import datetime
from telegram.ext import ConversationHandler
from mockups import MockUpdate, MockMessage, MockContext
from event import Event
from conversations.create_event import (evento, locandina, titolo, venue,
	data_inizio, orario_inizio, route_same_event)
from conversations.create_event import (LOCANDINA, TITOLO, LOCATION, 
	DATA_INIZIO, ORARIO_INIZIO, ROUTE_SAME_EVENT, DATA_FINE)


def test_evento():
	# evento gets executed when the command /evento
	# is sent to the bot. There's no special edge-case to test 
	update = MockUpdate(MockMessage())
	context = MockContext()
	assert evento(update, context) == LOCANDINA


def test_locandina():
	update = MockUpdate(MockMessage())
	context = MockContext()
	assert locandina(update, context) == TITOLO


def test_titolo():
	update = MockUpdate(MockMessage('nome evento'))
	context = MockContext()
	assert titolo(update, context) == LOCATION


def test_venue():
	update = MockUpdate(MockMessage('nome venue'))
	context = MockContext()
	assert venue(update, context) == DATA_INIZIO


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
