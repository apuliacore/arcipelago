CREATE TABLE event (
	id INTEGER PRIMARY KEY AUTOINCREMENT,
	name TEXT NOT NULL,
	venue TEXT NOT NULL,
	verified_venue_id INTEGER,
	start_datetime TIMESTAMP NOT NULL,
	end_datetime TIMESTAMP,
	description TEXT NOT NULL,
	confirmed BOOL NOT NULL DEFAULT False,
	published BOOL NOT NULL DEFAULT False,
	price REAL,
	categories TEXT,
	from_chat INTEGER,
	telegram_link TEXT,
	publication_date DATE,
	FOREIGN KEY (verified_venue_id) REFERENCES venue (id)
);

PRAGMA user_version = 2;
