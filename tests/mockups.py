from event import Event
from dataclasses import dataclass


class MockPhoto:
	def __init__(self):
		self.file_id = 0


@dataclass
class MockUser:
	username: str = 'marco123'
	first_name: str = 'Marco'


class MockMessage:
	def __init__(self, text='Hello world!'):
		self.text = text
		self.photo = [MockPhoto()]
		self.from_user = MockUser()

	def reply_text(self, text, reply_markup=None):
		print(text)

	def reply_photo(self, photo, caption, parse_mode=None):
		print(caption)


class MockUpdate:
	def __init__(self, msg):
		self.message = msg


class MockContext:
	def __init__(self, event=Event()):
		self.user_data = dict()
		self.user_data['event'] = event
		self.user_data['locandina'] = None
