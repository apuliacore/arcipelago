from arcipelago.conversations.send_feedback import feedback, ask_anon, send_feedback_anonymously, send_feedback_identified
from arcipelago.conversations.send_feedback import ASK_ANON, SEND_FEEDBACK, SEND_ANON
from mockups import MockUser, MockMessage, MockUpdate, MockContext


def test_feedback():
	update = MockUpdate(MockMessage('/feedback'))
	context = MockContext()
	assert feedback(update, context) == ASK_ANON


def test_ask_anon():
	anon_user = MockUser()
	anon_user.username = None
	update = MockUpdate(MockMessage('Some user feedback.', anon_user))
	context = MockContext()
	assert ask_anon(update, context) == SEND_ANON

	ident_user = MockUser()
	update = MockUpdate(MockMessage('Some user feedback.', ident_user))
	assert ask_anon(update, context) == SEND_FEEDBACK
