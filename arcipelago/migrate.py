import db


def main():
	current_version = db.get_db_version()
	if current_version < 2:
		migrate_v1_v2()


def migrate_v1_v2():
	print("Migrating from db version 1 to version 2.")

	db_connection = db.get_connection()
	cursor = db_connection.cursor()

	cursor.execute('ALTER TABLE event RENAME TO event_old')
	with open('schema_v2.sql', 'rb') as f:
		cursor.executescript(f.read().decode('utf8'))
	events = cursor.execute('SELECT * FROM event_old').fetchall()
	for event in events:
		cursor.execute('INSERT INTO event (name, venue, verified_venue_id, \
					   start_datetime, end_datetime, description, confirmed, \
					   published, price, categories) \
					   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)',
					   event[1:])
		db_connection.commit()
	cursor.execute('DROP TABLE event_old')
	db_connection.commit()


if __name__ == '__main__':
	main()