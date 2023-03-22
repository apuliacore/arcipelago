import datetime

from apuliacore_bot.db import insert_event, get_connection, set_published, get_events_next_n_days_not_published, get_events_in_date, get_event_from_id, get_event_from_hash, delete_event
from apuliacore_bot.event import Event


def get_dummy_event():
	event = Event()
	event.name = 'Martedì Popolare'
	event.venue = 'Storie del Vecchio Sud, via Buccari, Bari'
	event.start_datetime = datetime.datetime(2022, 9, 10, 21, 0)
	event.end_datetime = datetime.datetime(2022, 9, 10, 23, 0)
	event.description = 'Un gruppo di amici che si riunisce ogni due martedì per tenere viva la tradizione musicale popolare della nostra terra.'
	event.categories = 'musica, arte'
	return event


def test_insert_event():
	event = get_dummy_event()
	event_id = insert_event(event)
	db_conn = get_connection()
	cursor = db_conn.cursor()
	res = cursor.execute("SELECT * FROM event WHERE name = 'Martedì Popolare'").fetchone()
	db_conn.close()
	assert res[1:] == ('Martedì Popolare', 'Storie del Vecchio Sud, via Buccari, Bari', None, 
		datetime.datetime(2022, 9, 10, 21, 0), datetime.datetime(2022, 9, 10, 23, 0), 
		'Un gruppo di amici che si riunisce ogni due martedì per tenere viva la tradizione musicale popolare della nostra terra.', False, False, 0, 'musica, arte')
	delete_event(event_id)


def test_set_published():
	set_published(1)
	db_conn = get_connection()
	cursor = db_conn.cursor()
	res = cursor.execute("SELECT * FROM event WHERE id = 1").fetchone()
	assert res[8] ==  True  # confrimed is the 9th field
	cursor.execute("UPDATE event SET published=False WHERE id=(?)", (1,))
	db_conn.commit()
	db_conn.close()


def test_get_events_next_n_days_not_published():
	res = get_events_next_n_days_not_published()
	assert len(res) == 0


def test_get_events_in_date():
	date = datetime.datetime(2022, 10, 10, 0, 0, 0)
	res = get_events_in_date(date)
	assert len(res) == 1


def test_format_res_html():
	res = get_event_from_id(1)[0]
	event = Event()
	res_html = event.load_from_res(res).html()
	assert "Estate</code>" in res_html


def test_event_hash():
	res = get_event_from_id(1)[0]
	event = Event()
	event.load_from_res(res)
	res = get_event_from_hash(event.hash())
	assert event.name == res[0][1]  # <- event name


def test_delete_event():
	event = get_dummy_event()
	event_id = insert_event(event)
	delete_event(event_id)
	event_res = get_event_from_id(event_id)
	assert event_res == []
