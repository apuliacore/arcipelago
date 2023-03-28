from telegram.ext import ConversationHandler
from conversations.edit_event import edit, edit_field, confirm_edit_field
from conversations.edit_event import EDIT2, EDIT3
from mockups import MockUpdate, MockMessage, MockContext
import arcipelago


def test_edit():
	# wrong command usage
	update = MockUpdate(MockMessage(text='/modifica'))
	context = MockContext()
	assert edit(update, context) == ConversationHandler.END

	# event not found
	update = MockUpdate(MockMessage(text='1234'))
	assert edit(update, context) == ConversationHandler.END	

	update = MockUpdate(MockMessage(text='-4867727275918323885'))  # corso di ballo
	# '6207925744759765552'  # phest
	assert edit(update, context) == EDIT2


def test_edit_field():
	# non-editable field
	update = MockUpdate(MockMessage(text='Locandina'))
	context = MockContext()
	assert edit_field(update, context) == EDIT2

	# editable field
	update = MockUpdate(MockMessage(text='Luogo'))
	assert edit_field(update, context) == EDIT3


def test_confirm_edit_field():
	event = arcipelago.event.Event()
	event.load_from_res(arcipelago.db.get_event_from_id(3)[0])
	
	update = MockUpdate(MockMessage('PhEST 2022 | Opening Days'))
	context = MockContext()
	context.user_data['field_to_edit'] = 'Nome'
	context.user_data['event_to_edit'] = event

	assert confirm_edit_field(update, context) == ConversationHandler.END
