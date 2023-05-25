"""Main conversation used to create a new event."""


import traceback
import telegram
from telegram import InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import CommandHandler, CallbackQueryHandler, ConversationHandler, MessageHandler
from telegram.ext.filters import Filters as F
from arcipelago.config import notification_channel, authorized_users, chatbot_token
from arcipelago.db import insert_event, set_confirmed, get_event_from_id
from arcipelago.event import category2emoji, Event, check_events_collision, BadEventAttrError
from arcipelago.notification import check_event_will_get_published, publish_event
from arcipelago.conversations import text
from arcipelago.conversations import keyboards as K
from tests.mockups import MockBot


(STORE_POSTER, STORE_EVENT_NAME, STORE_EVENT_TYPE, STORE_EVENT_VENUE,
 ASK_START_DATE, ASK_START_TIME, ASK_END_DATE,
 ASK_END_TIME_PATH_END_DATE, ASK_ADD_END_DATE, ASK_END_TIME_PATH_NO_END_DATE,
 STORE_END_DATE, STORE_OPENING_HOURS, STORE_NUM_EVENTS, STORE_EVENT_VENUES_CALENDAR,
 STORE_START_DATES_CALENDAR, STORE_START_TIMES_CALENDAR, STORE_EVENTS_DURATION_CALENDAR,
 ASK_CATEGORY_PATH_END_TIME, ASK_DESCRIPTION, ASK_PUBLICATION_DATE, ASK_CONFIRM_SUBMISSION,
 PROCESS_EVENT, ROUTE_SAME_EVENT) = range(23)


if chatbot_token:
    bot = telegram.Bot(token=chatbot_token)
else:
    bot = MockBot(token=chatbot_token)


def ask_poster(update, context) -> int:
    """Starts adding an event asking for picture of event"""
    update.message.reply_text(text.poster)
    context.user_data['event'] = Event()
    context.user_data['event'].from_chat = update.message.from_user.id
    return STORE_POSTER


def store_poster(update, context) -> int:
    """Stores the photo and asks event name."""
    photo_file = update.message.photo[-1].file_id
    context.user_data['locandina'] = photo_file
    update.message.reply_text(text.ask_event_name)
    return STORE_EVENT_NAME


def store_event_name(update, context) -> int:
    """Stores event name and asks event type."""
    try:
        context.user_data['event'].name = update.message.text
        update.message.reply_text(text.ask_event_type, reply_markup=K.event_type)
        return STORE_EVENT_TYPE
    except BadEventAttrError as e:
        update.message.reply_text(str(e))
        return STORE_EVENT_NAME


def store_event_venue(update, context) -> int:
    """Stores event venue and asks start date."""
    try:
        context.user_data['event'].venue = update.message.text
    except BadEventAttrError as e:
        update.message.reply_text(str(e))
        return STORE_EVENT_VENUE
    update.message.reply_text(text.ask_start_date)
    return ASK_START_TIME


def store_event_type(update, context) -> int:
    """Store event type and asks event venue(s)."""
    user_input = update.message.text.strip()
    if user_input not in K.event_types:
        update.message.reply_text(text.help_event_type)
        return STORE_EVENT_TYPE
    else:
        try:
            context.user_data['event'].event_type = user_input
        except BadEventAttrError as e:
            update.message.reply_text(str(e))
            return STORE_EVENT_TYPE

    if context.user_data['event'].event_type != 'Rassegna':
        update.message.reply_text(text.ask_venue_name)
        return STORE_EVENT_VENUE
    else:
        update.message.reply_text(text.ask_num_events)
        return STORE_NUM_EVENTS


def store_event_venues_calendar(update, context) -> int:
    """Stores events venues for a calendar of events."""
    user_input = update.message.text.strip()
    if ',' in user_input:
        venues = [venue.strip() for venue in user_input.split(',')]

        if len(venues) != len(context.user_data['calendar']):
            update.message.reply_text(text.ack_wrong_number_venues)
            return STORE_EVENT_VENUES_CALENDAR

        for event_idx, venue in enumerate(venues):
            try:
                context.user_data['calendar'][event_idx].venue = venue
            except BadEventAttrError as e:
                update.message.reply_text(str(e))
                return STORE_EVENT_VENUES_CALENDAR
    else:
        for event in context.user_data['calendar']:
            try:
                event.venue = user_input
            except BadEventAttrError as e:
                update.message.reply_text(str(e))
                return STORE_EVENT_VENUES_CALENDAR
    update.message.reply_text(text.ask_start_dates_calendar)
    return STORE_START_DATES_CALENDAR


def ask_start_date(update, context) -> int:
    """Stores event type and ask start date."""
    user_input = update.message.text.strip()
    if user_input not in K.event_types:
        update.message.reply_text(text.help_event_type)
        return ASK_START_DATE
    else:
        try:
            context.user_data['event'].event_type = user_input

            if context.user_data['event'].event_type != 'Rassegna':
                update.message.reply_text(text.ask_start_date)
                return ASK_START_TIME
            else:
                update.message.reply_text(text.ask_num_events)
                return STORE_NUM_EVENTS
        except BadEventAttrError as e:
            update.message.reply_text(str(e))
            return ASK_START_DATE


def store_num_events(update, context) -> int:
    """Creates a list of events based on the user input."""
    try:
        num_events = int(update.message.text.strip())
    except ValueError:
        update.message.reply_text("Formato non valido, invia un singolo numero:")
        return STORE_NUM_EVENTS

    if num_events < 2:
        update.message.reply_text(text.ack_wrong_number_events)
        return STORE_NUM_EVENTS
    else:
        context.user_data['calendar'] = [Event()]*num_events
        update.message.reply_text(text.ask_event_venues_calendar)
        return STORE_EVENT_VENUES_CALENDAR


def store_start_dates_calendar(update, context) -> int:
    """Stores start dates for a calendar of events."""
    user_input = update.message.text.strip()
    if ',' in user_input:
        dates = [date.strip() for date in user_input.split(',')]

        if len(dates) != len(context.user_data['calendar']):
            update.message.reply_text(text.ack_wrong_number_dates)
            return STORE_START_DATES_CALENDAR

        for event_idx, date in enumerate(dates):
            try:
                context.user_data['calendar'][event_idx].start_date = date
            except BadEventAttrError as e:
                update.message.reply_text(str(e))
                return STORE_START_DATES_CALENDAR
    else:
        for event in context.user_data['calendar']:
            try:
                event.start_date = user_input
            except BadEventAttrError as e:
                update.message.reply_text(str(e))
                return STORE_START_DATES_CALENDAR
    update.message.reply_text(text.ask_start_times_calendar)
    return STORE_START_TIMES_CALENDAR


def store_start_times_calendar(update, context) -> int:
    """Stores start times for a calendar of events."""
    user_input = update.message.text.strip()
    if ',' in user_input:
        start_times = [time.strip() for time in user_input.split(',')]

        if len(start_times) != len(context.user_data['calendar']):
            update.message.reply_text(text.ack_wrong_number_start_times)
            return STORE_START_TIMES_CALENDAR

        for event_idx, time in enumerate(start_times):
            try:
                context.user_data['calendar'][event_idx].start_time = time
            except BadEventAttrError as e:
                update.message.reply_text(str(e))
                return STORE_START_TIMES_CALENDAR
    else:
        for event in context.user_data['calendar']:
            try:
                event.start_time = user_input
            except BadEventAttrError as e:
                update.message.reply_text(str(e))
                return STORE_START_TIMES_CALENDAR
    update.message.reply_text(text.ask_events_duration_calendar)
    return STORE_EVENTS_DURATION_CALENDAR


def store_events_duration_calendar(update, context) -> int:
    """Stores durations of events in a calendar of events."""
    user_input = update.message.text.strip()
    if ',' in user_input:
        try:
            durations = [int(duration.strip()) for duration in user_input.split(',')]
        except ValueError:
            update.message.reply_text("Formato non valido.")
            update.message.reply_text(text.ask_events_duration_calendar)

        if len(durations) != len(context.user_data['calendar']):
            update.message.reply_text(text.ack_wrong_number_durations)
            return STORE_EVENTS_DURATION_CALENDAR

        for event_idx, event_duration in enumerate(durations):
            try:
                context.user_data['calendar'][event_idx].set_duration(event_duration)
            except BadEventAttrError as e:
                update.message.reply_text(str(e))
                return STORE_EVENTS_DURATION_CALENDAR
    else:
        try:
            event_duration = int(update.message.text.strip())
        except ValueError:
            update.message.reply_text("Formato non valido.")
            update.message.reply_text(text.ask_events_duration_calendar)

        for event in context.user_data['calendar']:
            try:
                event.set_duration(event_duration)
            except BadEventAttrError as e:
                update.message.reply_text(str(e))
                return STORE_EVENTS_DURATION_CALENDAR
    update.message.reply_text(text.ask_category, reply_markup=K.category)
    return ASK_DESCRIPTION


def ask_start_time(update, context) -> int:
    """Stores start date and asks start time."""
    try:
        context.user_data['event'].start_date = update.message.text
    except BadEventAttrError as e:
        update.message.reply_text(str(e))
        return ASK_START_TIME
    if context.user_data['event'].event_type == 'Evento singolo':
        update.message.reply_text(text.ask_start_time)
        return ASK_ADD_END_DATE
    elif context.user_data['event'].event_type == 'Esposizione':
        update.message.reply_text(text.ask_end_date)
        return STORE_END_DATE


def ask_add_end_date(update, context) -> int:
    """Stores start time, checks if there is already a similar event,
    if not asks if user wants to add end date."""
    try:
        context.user_data['event'].start_time = update.message.text
        colliding_event = check_events_collision(context.user_data['event'])
        if colliding_event is not None:
            update.message.reply_text(text.similar_event)
            update.message.reply_text(colliding_event.html(), parse_mode=telegram.ParseMode.HTML)
            update.message.reply_text(text.ask_same_event, reply_markup=K.yes_or_no)
            return ROUTE_SAME_EVENT
        else:
            if context.user_data['event'].event_type == 'Evento singolo':
                update.message.reply_text(text.ask_event_duration)
                return ASK_CATEGORY_PATH_END_TIME
            else:
                update.message.reply_text(text.ask_add_end_date, reply_markup=K.yes_or_no)
                return ASK_END_DATE
    except BadEventAttrError as e:
        update.message.reply_text(str(e))
        return ASK_ADD_END_DATE


def route_same_event(update, context) -> int:
    """Routes conversation based on whether the event is the same."""
    user_input = update.message.text.strip().lower()
    if user_input == 'sì':
        update.message.reply_text(text.ack_same_event)
        return ConversationHandler.END
    elif user_input == 'no':
        if context.user_data['event'].event_type == 'Evento singolo':
            update.message.reply_text(text.ask_add_end_date, reply_markup=K.yes_or_no)
            return ASK_END_DATE
        elif context.user_data['event'].event_type == 'Esposizione':
            update.message.reply_text(text.ask_category, reply_markup=K.category)
            return ASK_DESCRIPTION


def ask_end_date(update, context) -> int:
    """Asks for ending date."""
    update.message.reply_text(text.ask_end_date)
    return ASK_END_TIME_PATH_END_DATE


def store_end_date(update, context) -> int:
    try:
        context.user_data['event'].end_date = update.message.text
    except BadEventAttrError as e:
        update.message.reply_text(str(e))
        return STORE_END_DATE
    if context.user_data['event'].event_type == 'Esposizione':
        update.message.reply_text(text.ask_opening_hours)
        return STORE_OPENING_HOURS


def store_opening_hours(update, context) -> int:
    """Stores opening hours for an exposition."""
    if '-' in update.message.text:
        opening_time, closing_time = update.message.text.split('-')
        opening_time, closing_time = opening_time.strip(), closing_time.strip()
        try:
            context.user_data['event'].start_time = opening_time
            context.user_data['event'].end_time = closing_time
        except BadEventAttrError as e:
            update.message.reply_text(str(e))
            update.message.reply_text(text.ask_opening_hours)
            return STORE_OPENING_HOURS

        colliding_event = check_events_collision(context.user_data['event'])
        if colliding_event is not None:
            update.message.reply_text(text.similar_event)
            update.message.reply_text(colliding_event.html(), parse_mode=telegram.ParseMode.HTML)
            update.message.reply_text(text.ask_same_event, reply_markup=K.yes_or_no)
            return ROUTE_SAME_EVENT
        else:
            update.message.reply_text(text.ask_category, reply_markup=K.category)
            return ASK_DESCRIPTION
    else:
        update.message.reply_text('Formato non valido.')
        update.message.reply_text(text.ask_opening_hours)
        return STORE_OPENING_HOURS


def ask_end_time_path_end_date(update, context) -> int:
    """Stores ending date and asks ending time."""
    try:
        context.user_data['event'].end_date = update.message.text
        update.message.reply_text(text.ask_end_time)
        return ASK_CATEGORY_PATH_END_TIME
    except BadEventAttrError as e:
        update.message.reply_text(str(e))
        return ASK_END_TIME_PATH_END_DATE


def ask_add_end_time(update, context) -> int:
    """If the user chooses not to add an end date,
    the bot asks if he wants to add an end time."""
    update.message.reply_text(text.ask_add_end_time, reply_markup=K.yes_or_no)
    return ASK_END_TIME_PATH_NO_END_DATE


def ask_end_time_path_no_end_date(update, content) -> int:
    """If the user wants to add end time, the bot asks the end time."""
    update.message.reply_text(text.ask_end_time)
    return ASK_CATEGORY_PATH_END_TIME


def ask_category_path_end_time(update, context) -> int:
    """Stores end time and asks event category."""
    if context.user_data['event'].event_type == 'Evento singolo':
        try:
            event_duration = int(update.message.text.strip())
        except ValueError:
            update.message.reply_text("Formato non valido, invia un singolo numero:")
            return ASK_CATEGORY_PATH_END_TIME
        try:
            context.user_data['event'].set_duration(event_duration)
            update.message.reply_text(text.ask_category, reply_markup=K.category)
            return ASK_DESCRIPTION
        except BadEventAttrError as e:
            update.message.reply_text(str(e))
            return ASK_CATEGORY_PATH_END_TIME
    else:
        try:
            context.user_data['event'].end_time = update.message.text
            update.message.reply_text(text.ask_category, reply_markup=K.category)
            return ASK_DESCRIPTION
        except BadEventAttrError as e:
            update.message.reply_text(str(e))
            return ASK_CATEGORY_PATH_END_TIME


def ask_category_path_no_end_time(update, context) -> int:
    """If the users chooses not to add end time,
    the bot asks event category."""
    update.message.reply_text(text.ask_category, reply_markup=K.category)
    return ASK_DESCRIPTION


def ask_description(update, context) -> int:
    """Store event category and ask event description."""
    category = update.message.text[2:]
    if category not in category2emoji:
        update.message.reply_text(text.help_category, reply_markup=K.category)
        return ASK_DESCRIPTION
    context.user_data['event'].categories = category
    update.message.reply_text(text.ask_description)
    return ASK_PUBLICATION_DATE


def ask_publication_date(update, context) -> int:
    """Stores event description and asks the user
    the publication date for the event."""
    try:
        context.user_data['event'].description = update.message.text
        update.message.reply_text(text.ask_publication_date)
        return ASK_CONFIRM_SUBMISSION
    except BadEventAttrError as e:
        update.message.reply_text(str(e))
        return ASK_PUBLICATION_DATE


def ask_confirm_submission(update, context) -> int:
    """Stores publication date and asks the user to confirm
    the submission of the event."""
    try:
        context.user_data['event'].publication_date = update.message.text.strip()
    except BadEventAttrError as e:
        update.message.reply_text(str(e))
        return ASK_CONFIRM_SUBMISSION
    try:
        username = update.message.from_user.username
        first_name = update.message.from_user.first_name
        update.message.reply_photo(
            photo=context.user_data['locandina'],
            caption=context.user_data['event'].html(),
            parse_mode=telegram.ParseMode.HTML)
        update.message.reply_text(text.ask_confirm_send_event, reply_markup=K.yes_or_no)
        return PROCESS_EVENT
    except telegram.error.BadRequest:
        update.message.reply_text(text.send_event_failure)
        if username is not None:
            bot.sendMessage(chat_id=notification_channel, text=f"{first_name} (@{username}) ha provato ad inviare un evento ma si è verificato un errore")
        else:
            bot.sendMessage(chat_id=notification_channel, text=f"{first_name} ha provato ad inviare un evento ma si è verificato un errore")
        print(traceback.format_exc())
        return ConversationHandler.END


def process_submitted_event(update, context) -> int:
    """If the user is authorized, the event is stored in the DB.
    Otherwise, the event is sent to the admin notification channel
    where admins can approve it."""
    username = update.message.from_user.username
    first_name = update.message.from_user.first_name
    user_id = update.message.from_user.id
    event = context.user_data['event']

    if user_id in authorized_users:
        event.confirmed = True
        bot.send_photo(
                chat_id=notification_channel,
                photo=context.user_data['locandina'],
                caption=event.html(),
                parse_mode=telegram.ParseMode.HTML
            )
        if username is not None:
            bot.sendMessage(chat_id=notification_channel, text=f"Inviato da {first_name} (@{username}).")
        else:
            bot.sendMessage(chat_id=notification_channel, text=f"Inviato da {first_name}.")
        bot.sendMessage(chat_id=notification_channel, text=f"L'evento sarà pubblicato il {event.publication_date.strftime('%d.%m.%Y')}.")
        event.id = insert_event(event)
        file_locandina = bot.get_file(context.user_data['locandina'])
        file_locandina.download(f'locandine/{event.id}.jpg')
        update.message.reply_text(text.ack_event_accepted_admin)
        update.message.reply_text(f"Questo è il codice unico del tuo evento: <code>{event.hash()}</code>. "
            "Puoi usarlo con il comando /modifica per cambiare alcune informazioni sull'evento prima della pubblicazione.",
            parse_mode=telegram.ParseMode.HTML)
        if check_event_will_get_published(event) == False:
            publish_event(bot, event)
    else:
        bot.send_photo(
                chat_id=notification_channel,
                photo=context.user_data['locandina'],
                caption=event.html(),
                parse_mode=telegram.ParseMode.HTML
            )
        event.id = insert_event(event)
        file_locandina = bot.get_file(context.user_data['locandina'])
        file_locandina.download(f'locandine/{event.id}.jpg')

        if username is not None:
            bot.sendMessage(chat_id=notification_channel, text=f"Inviato da {first_name} (@{username}).")
        else:
            bot.sendMessage(chat_id=notification_channel, text=f"Inviato da {first_name}.")
        bot.sendMessage(chat_id=notification_channel, text=f"L'evento sarà pubblicato il {event.publication_date.strftime('%d.%m.%Y')}.")
        bot.sendMessage(chat_id=notification_channel, text=text.ask_confirm_publish_event,
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(text='Sì', callback_data=f"{user_id} {event.id} 1"),
                                                InlineKeyboardButton(text='No', callback_data=f"{user_id} {event.id} 0")]]))
        update.message.reply_text(text.ack_event_submitted)
    return ConversationHandler.END


def cancel(update, context) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text(text.ack_canceled_op)
    return ConversationHandler.END


event_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("evento", ask_poster)],
        states={
            STORE_POSTER: [MessageHandler(F.photo, store_poster)],
            STORE_EVENT_NAME: [MessageHandler(F.text & (~ F.command), store_event_name)],
            STORE_EVENT_TYPE: [MessageHandler(F.text, store_event_type)],
            STORE_EVENT_VENUE: [MessageHandler(F.text, store_event_venue)],
            ASK_START_DATE: [MessageHandler(F.text & (~ F.command), ask_start_date)],
            ASK_START_TIME: [MessageHandler(F.text, ask_start_time)],
            ROUTE_SAME_EVENT: [MessageHandler(F.text, route_same_event)],
            ASK_ADD_END_DATE: [MessageHandler(F.text, ask_add_end_date)],
            ASK_END_DATE: [MessageHandler(F.regex("Sì"), ask_end_date),
                        MessageHandler(F.regex("No"), ask_add_end_time)],
            STORE_END_DATE: [MessageHandler(F.text, store_end_date)],
            ASK_END_TIME_PATH_END_DATE: [MessageHandler(F.text, ask_end_time_path_end_date)],
            ASK_END_TIME_PATH_NO_END_DATE: [MessageHandler(F.regex("Sì"), ask_end_time_path_no_end_date),
                          MessageHandler(F.regex("No"), ask_category_path_no_end_time)],
            STORE_OPENING_HOURS: [MessageHandler(F.text, store_opening_hours)],
            STORE_NUM_EVENTS: [MessageHandler(F.text, store_num_events)],
            STORE_EVENT_VENUES_CALENDAR: [MessageHandler(F.text, store_event_venues_calendar)],
            STORE_START_DATES_CALENDAR: [MessageHandler(F.text, store_start_dates_calendar)],
            STORE_START_TIMES_CALENDAR: [MessageHandler(F.text, store_start_times_calendar)],
            STORE_EVENTS_DURATION_CALENDAR: [MessageHandler(F.text, store_events_duration_calendar)],
            ASK_CATEGORY_PATH_END_TIME: [MessageHandler(F.text, ask_category_path_end_time)],
            ASK_DESCRIPTION: [MessageHandler(F.text & (~ F.command), ask_description)],
            ASK_PUBLICATION_DATE: [MessageHandler(F.text & (~ F.command), ask_publication_date)],
            ASK_CONFIRM_SUBMISSION: [MessageHandler(F.text & (~ F.command), ask_confirm_submission)],
            PROCESS_EVENT: [MessageHandler(F.regex("Sì"), process_submitted_event),
                       MessageHandler(F.regex("No"), cancel)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )


def set_event_confirmation(update, context) -> None:
    """Called in response to pressing of InlineKeyboardButton. Either confirms or
    does not confirm an event."""
    callback_data = update.callback_query.data
    admin = update.callback_query.from_user
    user_id = int(callback_data.split()[0])
    event_id = int(callback_data.split()[1])
    confirmed = bool(int(callback_data.split()[2]))

    if confirmed:
        set_confirmed(event_id)
        event = Event().load_from_res(get_event_from_id(event_id)[0])
        update.callback_query.edit_message_text(text=f"Evento confermato da {admin.first_name} (@{admin.username}).")
        bot.sendMessage(chat_id=user_id, text=text.ack_event_accepted_user)
        bot.sendMessage(chat_id=user_id, text=f"Questo è il codice unico del tuo evento: <code>{event.hash()}</code>. "
            "Puoi usarlo con il comando /modifica per cambiare alcune informazioni sull'evento prima della pubblicazione.",
            parse_mode=telegram.ParseMode.HTML)
        if check_event_will_get_published(event) == False:
            publish_event(bot, event)
    else:
        update.callback_query.edit_message_text(text=f"Evento non confermato da {admin.first_name} (@{admin.username}).")
        bot.sendMessage(chat_id=user_id, text=text.ack_event_not_accepted)


callback_query_handler = CallbackQueryHandler(set_event_confirmation)
