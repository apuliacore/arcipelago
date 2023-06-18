"""Functions related to events data."""

import datetime
import html
import re
import difflib
import hashlib
from dataclasses import dataclass
from arcipelago.db import get_event_from_id, get_id_name_venue_start_dt_future_events


event_categories = ["musica", "cinema", "arte", "attivismo", "teatro e stand-up", "libri e lettura", "scienza e tecnologia", "fotografia", "danza", "fumetti e giochi", "altro"]
event_categories_emojis = ["🎹", "🎥", "🎨", "✊", "🎭", "📖", "🔭", "📷", "🩰", "👾", "❔"]
category2emoji = {c: e for c, e in zip(event_categories, event_categories_emojis)}


def get_event_str_repr(name: str, venue: str, start_datetime: datetime.datetime):
    return name.strip().lower() + venue.strip().lower() + start_datetime.strftime("%d.%m.%Y-%H:%M")


def check_events_collision(event):
    results = get_id_name_venue_start_dt_future_events()
    if results:
        str_repr2id = { get_event_str_repr(res[1], res[2], res[3]): res[0]
                        for res in results }
        closest_match = difflib.get_close_matches(event.get_str_repr(), str_repr2id.keys(), 1, cutoff=0.8)
        if closest_match:
            match_id = str_repr2id[closest_match[0]]
            event_res = get_event_from_id(match_id)[0]
            return Event().load_from_res(event_res)


class BadEventAttrError(Exception):
    pass


@dataclass
class Event(object):
    _id: int = None
    _name: str = ''
    _venue: str = ''
    _start_date: datetime.date = None
    _start_time: datetime.time = None
    _start_datetime: datetime.datetime = None
    _end_date: datetime.date = None
    _end_time: datetime.time = None
    _end_datetime: datetime.datetime = None
    _description: str = ''
    _confirmed: bool = False
    _published: bool = False
    _categories: str = ''
    _from_chat: int = None
    _telegram_link: str = ''
    _publication_date: datetime.date = None
    _event_type: str = ''

    @property
    def id(self):
        return self._id

    @property
    def name(self):
        return self._name

    @property
    def emoji(self):
        return category2emoji[self.categories] if self.categories else ""

    @property
    def venue(self):
        return self._venue

    @property
    def description(self):
        return self._description

    @property
    def start_date(self):
        return self._start_date

    @property
    def start_time(self):
        return self._start_time

    @property
    def start_datetime(self):
        return datetime.datetime.combine(self.start_date, self.start_time)

    @property
    def end_date(self):
        return self._end_date

    @property
    def end_time(self):
        return self._end_time

    @property
    def end_datetime(self):
        if self.end_date is not None and self.end_time is not None:
            return datetime.datetime.combine(self.end_date, self.end_time)
        elif self.end_time is not None:
            return datetime.datetime.combine(self.start_date, self.end_time)
        else:
            return None

    @property
    def from_chat(self):
        return self._from_chat

    @property
    def telegram_link(self):
        return self._telegram_link

    @property
    def publication_date(self):
        return self._publication_date

    @property
    def confirmed(self):
        return self._confirmed

    @property
    def published(self):
        return self._published

    @property
    def categories(self):
        return self._categories

    @property
    def event_type(self):
        return self._event_type

    @id.setter
    def id(self, value):
        self._id = value

    @name.setter
    def name(self, value):
        self._name = value

    @venue.setter
    def venue(self, value):
        self._venue = value

    @description.setter
    def description(self, value):
        self._description = value
        if len(self.html()) > 1024:  # limit of photo captions on Telegram
            self._description = ''
            raise BadEventAttrError("La descrizione dell'evento è troppo lunga per Telegram :/ Inviane una più breve.")
        else:
            self._description = value

    @categories.setter
    def categories(self, value):
        self._categories = value

    @confirmed.setter
    def confirmed(self, value):
        if isinstance(value, bool):
            self._confirmed = value
        elif isinstance(value, int):
            if value in [0, 1]:
                self._confirmed = int(value)
            else:
                raise BadEventAttrError(f"Accepted values for integer booleans are 0 or 1, not {value}")
        else:
            raise BadEventAttrError(f"Attribute confirmed should be of type {bool} or {int}, not {type(value)}")

    @published.setter
    def published(self, value):
        if isinstance(value, bool):
            self._published = value
        elif isinstance(value, int):
            if value in [0, 1]:
                self._published = int(value)
            else:
                raise BadEventAttrError(f"Accepted values for integer booleans are 0 or 1, not {value}")
        else:
            raise BadEventAttrError(f"Attribute published should be of type {bool} or {int}, not {type(value)}")

    @start_datetime.setter
    def start_datetime(self, value):
        if isinstance(value, datetime.datetime):
            self._start_datetime = value
            self._start_date = value.date()
            self._start_time = value.time()
        else:
            raise BadEventAttrError(f"Start datetime should be of type {datetime.datetime}, not {type(value)}")

    @start_date.setter
    def start_date(self, value):
        if isinstance(value, str):
            if re.match(r"((\d{2}|\d{1})(\.)(\d{2}|\d{1})(\.)\d{4})", value) is None:
                raise BadEventAttrError("La data che hai inserito ha un formato non valido. Manda una data in formato gg.mm.aaaa")
            else:
                dd, mm, yyyy = (int(t) for t in value.split('.'))
                input_date = datetime.date(day=dd, month=mm, year=yyyy)
                if input_date < datetime.datetime.now().date():
                    raise BadEventAttrError("La data che hai inserito è passata! Inserisci una data futura:")
                self._start_date = input_date
        elif isinstance(value, datetime.date):
            self._start_date = value
        else:
            raise BadEventAttrError(f"Start datetime should be of type {datetime.date} or {str}, not {type(value)}")

    @start_time.setter
    def start_time(self, value):
        if isinstance(value, str):
            if re.match(r"\d+:\d+", value) is None:
                raise BadEventAttrError("L'orario che hai inserito ha un formato non valido. Manda un orario in formato hh:mm")
            else:
                hh, mm = (int(t) for t in value.split(":"))
                if not (0 <= hh <= 23) or not (0 <= mm <= 59):
                    raise BadEventAttrError("L'orario che hai inserito non è valido. Inserisci un orario valido: [ore: 0-23, minuti: 0-59]")
                else:
                    start_time = datetime.time(hour=hh, minute=mm)
                    if datetime.datetime.combine(self.start_date, start_time) > datetime.datetime.now():
                        self._start_time = start_time
                    else:
                        raise BadEventAttrError("L'orario che hai inserito è passato! Inserisci un orario futuro:")
        elif isinstance(value, datetime.time):
            self._start_time = value
        else:
            raise BadEventAttrError(f"Start datetime should be of type {datetime.time} or {str}, not {type(value)}")

    @end_datetime.setter
    def end_datetime(self, value):
        if value is None:
            return
        if isinstance(value, datetime.datetime):
            self._end_datetime = value
            self._end_date = value.date()
            self._end_time = value.time()
        else:
            raise BadEventAttrError(f"End datetime should be of type {datetime.datetime}, not {type(value)}")

    @end_date.setter
    def end_date(self, value):
        if isinstance(value, str):
            if re.match(r"((\d{2}|\d{1})(\.)(\d{2}|\d{1})(\.)\d{4})", value) is None:
                raise BadEventAttrError("La data che hai inserito ha un formato non valido. Manda una data in formato gg.mm.aaaa")
            else:
                dd, mm, yyyy = (int(t) for t in value.split('.'))
                input_date = datetime.date(day=dd, month=mm, year=yyyy)
                if input_date < self.start_date:
                    raise BadEventAttrError("La data che hai inserito è precedente a quella di inzio evento. Inserisci una data successiva:")
                self._end_date = input_date
        elif isinstance(value, datetime.date):
            if value < self.start_date:
                raise BadEventAttrError("La data che hai inserito è precedente a quella di inzio evento. Inserisci una data successiva:")
            self._end_date = value
        else:
            raise BadEventAttrError(f"Start datetime should be of type {datetime.date} or {str}, not {type(value)}")

    @end_time.setter
    def end_time(self, value):
        if isinstance(value, str):
            if re.match(r"\d+:\d+", value) is None:
                raise BadEventAttrError("L'orario che hai inserito ha un formato non valido. Manda un orario in formato hh:mm")
            else:
                hh, mm = (int(t) for t in value.split(":"))
                if not (0 <= hh <= 23) or not (0 <= mm <= 59):
                    raise BadEventAttrError("L'orario che hai inserito non è valido. Inserisci un orario valido: [ore: 0-23, minuti: 0-59]")
                elif self.end_date is None or (self.end_date == self.start_date):
                    time_input = datetime.time(hour=hh, minute=mm)
                    if not self.start_time < time_input:
                        raise BadEventAttrError("L'orario che hai inserito è precedente a quello di inzio evento! Inserisci un orario valido:")
                    self._end_time = time_input
                elif self.event_type == 'Esposizione':
                    time_input = datetime.time(hour=hh, minute=mm)
                    virtual_end_datetime = datetime.datetime.combine(self.start_date, time_input)
                    if virtual_end_datetime < self.start_datetime:
                        raise BadEventAttrError("L'orario di chiusura dell'esposizione è predecedente all'orario di apertura. Inserisci degli orari validi:")
                    self._end_time = time_input
                else:
                    time_input = datetime.time(hour=hh, minute=mm)
                    self._end_time = time_input
        elif isinstance(value, datetime.time):
            if self.end_date is None or (self.end_date == self.start_date):
                if not self.start_time < value:
                    raise BadEventAttrError("L'orario che hai inserito è precedente a quello di inzio evento! Inserisci un orario valido:")
                self._end_time = value
            else:
                self._end_time = value
        else:
            raise BadEventAttrError(f"Start datetime should be of type {datetime.time} or {str}, not {type(value)}")

    @publication_date.setter
    def publication_date(self, value):
        if isinstance(value, str):
            if re.match(r"((\d{2}|\d{1})(\.)(\d{2}|\d{1})(\.)\d{4})", value) is None:
                raise BadEventAttrError("La data che hai inserito ha un formato non valido. Manda una data in formato gg.mm.aaaa")
            else:
                dd, mm, yyyy = (int(t) for t in value.split('.'))
                input_date = datetime.date(day=dd, month=mm, year=yyyy)
                date_today = datetime.datetime.now().date()
                if input_date < datetime.datetime.now().date():
                    raise BadEventAttrError("La data che hai inserito è passata! Inserisci una data futura:")
                elif input_date > self.start_date:
                    raise BadEventAttrError("La data che hai inserito è successiva alla data dell'evento! Inserisci una data precedente:")
                self._publication_date = input_date
        elif isinstance(value, datetime.date):
            if value > self.start_date:
                raise BadEventAttrError("La data che hai inserito è successiva alla data dell'evento! Inserisci una data precedente:")
            self._publication_date = value
        else:
            raise BadEventAttrError(f"Start datetime should be of type {datetime.date} or {str}, not {type(value)}")

    @from_chat.setter
    def from_chat(self, value):
        if isinstance(value, int):
            self._from_chat = value
        else:
            raise BadEventAttrError(f"from_chat should be of type int, not {type(value)}.")

    @telegram_link.setter
    def telegram_link(self, value):
        # TODO: add check link format
        if isinstance(value, str):
            self._telegram_link = value
        else:
            raise BadEventAttrError(f"telegram_link should be of type str not {type(value)}")

    @event_type.setter
    def event_type(self, value):
        if isinstance(value, str):
            self._event_type = value
        else:
            raise BadEventAttrError(f"event_type should be of type str not {type(value)}")

    def load_from_res(self, res):
        self.id = res[0]
        self.name = res[1]
        self.venue = res[2]
        self.start_datetime = res[4]
        self.start_date = res[4].date()
        self.start_time = res[4].time()
        self.end_datetime = res[5]
        if self.end_datetime is not None:
            self.end_date = res[5].date()
            self.end_time = res[5].time()
        self.description = res[6]
        self.confirmed = res[7]
        self.published = res[8]
        self.categories = res[10]
        if res[11] is not None:
            self.from_chat = res[11]
        if res[12] is not None:
            self.telegram_link = res[12]
        if res[13] is not None:
            self.publication_date = res[13]
        return self

    def html(self, short=False):
        start_datetime = self.start_datetime.strftime('%d.%m.%Y | %H:%M')
        start_date = self.start_datetime.strftime('%d.%m.%Y')
        start_time = self.start_datetime.strftime('%H:%M')

        if self.end_datetime is not None:
            if self.start_date == self.end_date:  # end same day different hour
                end_date = start_date
                end_datetime = self.end_time.strftime('%H:%M')
                end_time = end_datetime
            else:
                end_date = self.end_datetime.strftime('%d.%m.%Y')
                end_datetime = self.end_datetime.strftime('%d.%m.%Y | %H:%M')
                end_time = self.end_datetime.strftime('%H:%M')

        venue = self.venue
        description = html.escape(self.description)
        name = self.emoji + " " + self.name

        if short:
            res_html = f"🕒{start_time}"
            if self.end_datetime is not None:
                res_html +=  f" - {end_datetime}"
            res_html += f"""\n📍{venue}\n"""
            res_html += f"""<code>{name}</code>"""

        elif self.event_type == 'Esposizione':
            res_html = f"<code>{name}</code>\n"
            res_html += f"📅{start_date} - {end_date}"
            res_html += f"\n🕒{start_time} - {end_time}"
            res_html += f"""\n📍{venue}\n\n"""
            res_html += f"""{description}"""

        else:
            res_html = f"<code>{name}</code>\n"
            res_html += f"📅{start_datetime}"
            if self.end_datetime is not None:
                res_html +=  f" - {end_datetime}"
            res_html += f"""\n📍{venue}\n\n"""
            res_html += f"""{description}"""

        return res_html

    def hash(self):
        return str(hashlib.shake_128(self.name.encode()).hexdigest(5))

    def to_dict(self):
        return {
            'name': self.name,
            'venue': self.venue,
            'verified_venue_id': None ,
            'start_datetime': self.start_datetime,
            'end_datetime': self.end_datetime,
            'description': self.description,
            'confirmed': self.confirmed,
            'published': self.published,
            'price': 0,
            'categories': self.categories,
            'from_chat': self.from_chat,
            'telegram_link': None,
            'publication_date': self.publication_date,
        }

    def get_str_repr(self):
        return self.name.strip().lower() + self.venue.strip().lower() + self.start_datetime.strftime("%d.%m.%Y-%H:%M")

    def set_duration(self, duration: int):
        assert self.start_datetime is not None
        if duration < 1:
            raise BadEventAttrError("La durata minima per un evento è un'ora.")
        elif duration > 24:
            raise BadEventAttrError("La durata massima per un evento è 24 ore.")
        else:
            self.end_datetime = self.start_datetime + datetime.timedelta(hours=duration)


class Calendar(Event):
    def __init__(self):
        super().__init__()
        self.events = []

    @property
    def publication_date(self):
        return self._publication_date

    @publication_date.setter
    def publication_date(self, value):
        if isinstance(value, str):
            if re.match(r"((\d{2}|\d{1})(\.)(\d{2}|\d{1})(\.)\d{4})", value) is None:
                raise BadEventAttrError("La data che hai inserito ha un formato non valido. Manda una data in formato gg.mm.aaaa")
            else:
                dd, mm, yyyy = (int(t) for t in value.split('.'))
                input_date = datetime.date(day=dd, month=mm, year=yyyy)
                date_today = datetime.datetime.now().date()
                if input_date < datetime.datetime.now().date():
                    raise BadEventAttrError("La data che hai inserito è passata! Inserisci una data futura:")
                elif input_date > self.events[0].start_date:
                    raise BadEventAttrError("La data che hai inserito è successiva alla data dell'evento! Inserisci una data precedente:")
                self._publication_date = input_date
        elif isinstance(value, datetime.date):
            if value > self.events[0].start_date:
                raise BadEventAttrError("La data che hai inserito è successiva alla data dell'evento! Inserisci una data precedente:")
            self._publication_date = value
        else:
            raise BadEventAttrError(f"Start datetime should be of type {datetime.date} or {str}, not {type(value)}")

    def html(self):
        name = self.emoji + " " + self.name

        res_html = f"<code>{name}</code>\n"

        for event in self.events:
            start_datetime = event.start_datetime.strftime('%d.%m.%Y | %H:%M')
            res_html += f"📅{start_datetime}"
            res_html += f"""\n📍{event.venue}\n\n"""

        description = html.escape(self.description)
        res_html += f"""{description}"""
        return res_html
