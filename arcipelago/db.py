import sqlite3
import datetime
import hashlib


def init_db(development=False):
	db_connection = sqlite3.connect(
		"arcipelago.db",
		detect_types=sqlite3.PARSE_DECLTYPES
	)	

	cursor = db_connection.cursor()

	cursor.execute("DROP TABLE IF EXISTS event;")
	db_connection.commit()
	
	cursor.execute("DROP TABLE IF EXISTS event_old;")
	db_connection.commit()
	
	cursor.execute("DROP TABLE IF EXISTS venue;")
	db_connection.commit()

	with open('schema_v2.sql', 'rb') as f:
		cursor.executescript(f.read().decode('utf8'))

	if development:
		with open('dummy.sql', 'rb') as f:
			cursor.executescript(f.read().decode('utf8'))

	db_connection.close()


def import_db():
	from arcipelago.event import Event, BadEventAttrError
	
	path_db_file = input("Enter path to db file:")
	events = read_events(path_db_file)
	
	for event in events:
		try:
			insert_event(Event().load_from_res(event))
		except BadEventAttrError:
			print(f'Could not load event {event[0]} {event[1]}')


def read_events(db_name):
	conn = sqlite3.connect(
		db_name,
		detect_types=sqlite3.PARSE_DECLTYPES
	)
	cursor = conn.cursor()
	events = cursor.execute("SELECT * FROM event").fetchall()
	return events


def get_connection():
	return sqlite3.connect(
			"arcipelago.db",
			detect_types=sqlite3.PARSE_DECLTYPES
		)


def insert_event(event):
	event_dict = event.to_dict()
	execute_query(
		"INSERT INTO event (name, venue, verified_venue_id,\
		 start_datetime, end_datetime, publication_date, description, confirmed, published, price, categories)\
		 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
		(event_dict['name'],
		 event_dict['venue'],
		 event_dict['verified_venue_id'],
		 event_dict['start_datetime'],
		 event_dict['end_datetime'],
		 event_dict['publication_date'],
		 event_dict['description'],
		 event_dict['confirmed'],
		 event_dict['published'],
		 event_dict['price'],
		 event_dict['categories'])
	)
	return get_id_last_added_in_table('event')[0][0]


def get_event_from_id(event_id: int):
	return execute_select_query("SELECT * FROM event WHERE id=(?)", (event_id,))


def set_published(event_id: int):
	execute_query("UPDATE event SET published=True WHERE id=(?)", (event_id,))


def set_confirmed(event_id: int):
	execute_query("UPDATE event SET confirmed=True WHERE id=(?)", (event_id,))


def get_id_last_added_in_table(table_name: str):
	return execute_select_query("SELECT seq FROM sqlite_sequence WHERE name=(?)", (table_name,))


def get_events_next_n_days_not_published(n_days=7):
	datetime_now = datetime.datetime.now()
	datetime_n_days_from_now = datetime_now + datetime.timedelta(days=n_days)
	return execute_select_query(
		"SELECT * FROM event WHERE start_datetime > ? AND start_datetime < ? AND published = False AND confirmed = True",
		(datetime_now, datetime_n_days_from_now)
	)


def get_events_to_be_published_today():
	date_now = datetime.datetime.now().date()
	return execute_select_query(
		"SELECT * FROM event WHERE publication_date = ? AND published = False AND confirmed = True",
		(date_now,)
	)


def get_id_name_venue_start_dt_future_events():
	datetime_now = datetime.datetime.now()
	return execute_select_query(
		"SELECT id, name, venue, start_datetime FROM event WHERE start_datetime > ?",
		(datetime_now, )
	)

def get_events_in_date(event_datetime: datetime.datetime):
	event_date = event_datetime.date()
	return execute_select_query(
		"SELECT * FROM event WHERE date(start_datetime) = ? and confirmed = True ORDER BY start_datetime",
		(event_date,)
	)


def get_event_from_hash(event_hash: str):

	def get_event_hash(name: str):
	    name_hash = hashlib.shake_128(name.encode()).hexdigest(5)
	    return str(name_hash)

	db_connection = sqlite3.connect(
			"arcipelago.db",
			detect_types=sqlite3.PARSE_DECLTYPES
		)
	db_connection.create_function("get_event_hash", 1, get_event_hash)
	cursor = db_connection.cursor()
	res = cursor.execute("SELECT * FROM event WHERE get_event_hash(name) = ? AND published = False", (event_hash,)).fetchall()
	db_connection.close()
	return res


def edit_event(event_id: int, field_to_edit: str, new_field_value):
	execute_query(f"UPDATE event SET {field_to_edit} = ? WHERE id = ? and published=False", (new_field_value, event_id,))


def delete_event(event_id: int):
	execute_query("DELETE FROM event WHERE id = ?", (event_id, ))


def execute_query(query, values):
	db_connection = get_connection()
	cursor = db_connection.cursor()
	cursor.execute(query, values)
	db_connection.commit()
	db_connection.close()


def execute_select_query(query, values):
	db_connection = get_connection()
	cursor = db_connection.cursor()
	res = cursor.execute(query, values).fetchall()
	db_connection.close()
	return res

def get_db_version():
	db_connection = get_connection()
	cursor = db_connection.cursor()
	res = cursor.execute('PRAGMA user_version').fetchall()
	return res[0][0]
