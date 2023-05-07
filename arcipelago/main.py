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
from arcipelago.db import get_events_in_date
from arcipelago.event import Event
from arcipelago.config import chatbot_token, notification_channel, daily_update_interval
from arcipelago.conversations.create_event import event_conv_handler, callback_query_handler
from arcipelago.conversations.edit_event import edit_conv_handler
from arcipelago.conversations.send_feedback import feedback_conv_handler
from arcipelago.conversations import text
from arcipelago.notification import daily_publication_callback, get_next_hour_datetime, daily_events_callback


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


def dona(update, context) -> int:
    """Shows info about making a donation."""
    update.message.reply_text(text.intro_donate)
    update.message.reply_text(text.info_donate)
    update.message.reply_text(text.link_donate)
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
    donation_handler = CommandHandler("dona", dona)
    disp.job_queue.run_repeating(daily_publication_callback, interval=daily_update_interval, first=get_next_hour_datetime(10))
    disp.job_queue.run_repeating(daily_events_callback, interval=60*60*24, first=get_next_hour_datetime(17))
    disp.add_handler(start_handler)
    disp.add_handler(event_conv_handler)
    disp.add_handler(edit_conv_handler)
    disp.add_handler(todays_events_handler)
    disp.add_handler(feedback_conv_handler)
    disp.add_handler(callback_query_handler)
    disp.add_handler(donation_handler)
    upd.start_polling()
    upd.idle()


if __name__ == '__main__':
    main()
