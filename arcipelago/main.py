import telegram
from telegram import Update
from telegram.ext import (
    Updater,
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)
import datetime
import re
from db import get_events_in_date
from event import Event
from config import chatbot_token, notification_channel, daily_update_interval
from conversations.create_event import event_conv_handler, callback_query_handler
from conversations.edit_event import edit_conv_handler
from conversations import text
from notification import daily_publication_callback, get_next_hour_datetime, daily_events_callback


TOKEN = chatbot_token


def start(update, context) -> int:
    """Starts the conversation."""
    update.message.reply_text(text.welcome)
    return ConversationHandler.END


def oggi(update, context) -> int:
    """Returns today's events."""
    now = datetime.datetime.now()
    todays_events = [Event().load_from_res(e) for e in get_events_in_date(now)]
    if len(todays_events) > 0:
        update.message.reply_text("\n\n".join([f"Eventi di oggi {now.strftime('%d.%m.%Y')}"] + [event.html(short=True) for event in todays_events]),
                                  parse_mode=telegram.ParseMode.HTML)
    else:
        update.message.reply_text(text.no_event)
    return ConversationHandler.END


def giorno(update, context) -> int:
    """Returns a specific date's events."""
    if update.message.text.strip() == "/giorno":
        update.message.reply_text("Inserisci la data dopo il comando, ad esempio così: /giorno 17.02.2023")
    else :
        date_selected = datetime.datetime.strptime(update.message.text[8:], '%d.%m.%Y')
        selected_date_events = [Event().load_from_res(e) for e in get_events_in_date(date_selected)]
        if len(selected_date_events) > 0:
            update.message.reply_text("\n\n".join([f"Eventi di oggi {date_selected.strftime('%d.%m.%Y')}"] + [event.html(short=True) for event in selected_date_events]),
                                    parse_mode=telegram.ParseMode.HTML)
        else:
            update.message.reply_text(text.no_event)
    return ConversationHandler.END


def feedback(update, context) -> int:
    """Sends feedback message to admins group."""
    if update.message.text.strip() == "/feedback":
        update.message.reply_text(text.help_feedback)
    else:
        telegram.Bot(token=TOKEN).sendMessage(chat_id=notification_channel, text=update.message.text[10:])
        update.message.reply_text(text.ack_feedback_received)
    return ConversationHandler.END


def cancel(update, context) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text(text.ack_canceled_op)
    return ConversationHandler.END


def main():
    upd = Updater(TOKEN, use_context=True)
    disp = upd.dispatcher
    
    start_handler = CommandHandler("start", start)
    todays_events_handler = CommandHandler("oggi", oggi)
    giorno_handler = CommandHandler("giorno", giorno)
    feedback_handler = CommandHandler("feedback", feedback)
    disp.job_queue.run_repeating(daily_publication_callback, interval=daily_update_interval, first=get_next_hour_datetime(10))
    disp.job_queue.run_repeating(daily_events_callback, interval=60*60*24, first=get_next_hour_datetime(17))
    disp.add_handler(start_handler)
    disp.add_handler(event_conv_handler)
    disp.add_handler(edit_conv_handler)
    disp.add_handler(todays_events_handler)
    disp.add_handler(feedback_handler)
    disp.add_handler(callback_query_handler)
    disp.add_handler(giorno_handler)
    upd.start_polling()
    upd.idle()


if __name__ == '__main__':
    main()
