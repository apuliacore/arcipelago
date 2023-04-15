import telegram
from telegram.ext import ConversationHandler, filters, CommandHandler, MessageHandler
from arcipelago.db import edit_event, get_event_from_hash
from arcipelago.event import Event
from arcipelago.conversations import text
from arcipelago.conversations import keyboards as K


(EDIT2, EDIT3) = range(2)


def edit(update, context) -> int:
    """Allows the user to modify information of an event."""
    if update.message.text.strip() == "/modifica":
        update.message.reply_text(text.help_edit)
        return ConversationHandler.END
    else:
        event_hash = update.message.text.strip()[10:]
        event = Event()
        event_res = get_event_from_hash(event_hash)
        if event_res:
            event.load_from_res(event_res[0])
            context.user_data['event_to_edit'] = event
            update.message.reply_text(text.ack_edit_event)
            update.message.reply_text(event.html(), parse_mode=telegram.ParseMode.HTML)
            update.message.reply_text(text.ask_edit_field, reply_markup=K.editable)
            return EDIT2
        else:
            update.message.reply_text(text.edit_event_failure)
            return ConversationHandler.END


def edit_field(update, context) -> int:
    """Modify specific information for an event."""
    if update.message.text not in K.editable_fields:
        update.message.reply_text(text.help_edit_field, reply_markup=K.editable)
        return EDIT2
    else:
        context.user_data['field_to_edit'] = update.message.text
        update.message.reply_text(text.ask_new_value_field)
        return EDIT3


def confirm_edit_field(update, context) -> int:
    """Actually modify the field if the new value is acceptable."""
    user_input = update.message.text
    error_str = ''
    field = context.user_data['field_to_edit']
    event = context.user_data['event_to_edit']
    
    try:
        if field == "Data inizio":
            event.start_date = user_input
            updated_value = event.start_datetime
        elif field == "Data fine":
            event.end_date = user_input
            updated_value = event.end_datetime
        elif field == "Ora inizio":
            event.start_time = user_input
            updated_value = event.start_datetime
        elif field == "Ora fine":
            event.end_time = user_input
            updated_value = event.end_datetime
        elif field == 'Descrizione':
            event.description = user_input
            updated_value = event.description
        elif field == 'Nome':
            event.name = user_input
            updated_value = event.name
        elif field == 'Luogo':
            event.venue = user_input
            updated_value = event.venue

    except Exception as e:
        update.message.reply_text(str(e))
        return EDIT3

    field_to_db_name = {
        "Nome": "name",
        "Luogo": "venue",
        "Data inizio": "start_datetime",
        "Ora inizio": "start_datetime",
        "Data fine": "end_datetime",
        "Ora fine": "end_datetime",
        "Descrizione": "description"
    }
    db_field = field_to_db_name[field]
    edit_event(event.id, db_field, updated_value)
    update.message.reply_text(text.ack_event_modified)
    update.message.reply_text(event.html(), parse_mode=telegram.ParseMode.HTML)
    update.message.reply_text(f"Il nuovo codice del tuo evento è <code>{event.hash()}</code>.", parse_mode=telegram.ParseMode.HTML)

    return ConversationHandler.END


def cancel(update, context) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text(text.ack_canceled_op)
    return ConversationHandler.END


edit_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("modifica", edit)],
        states={
            EDIT2: [MessageHandler(filters.Filters.text & (~ filters.Filters.command), edit_field)],
            EDIT3: [MessageHandler(filters.Filters.text & (~ filters.Filters.command), confirm_edit_field)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
)
    