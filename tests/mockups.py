from event import Event


class MockPhoto:
	def __init__(self):
		self.file_id = 0


class MockMessage:
	def __init__(self, text='Hello world!'):
		self.text = text
		self.photo = [MockPhoto()]

	def reply_text(self, text, reply_markup=None):
		print(text)


class MockUpdate:
	def __init__(self, msg):
		self.message = msg


class MockContext:
	def __init__(self, event=Event()):
		self.user_data = dict()
		self.user_data['event'] = event
