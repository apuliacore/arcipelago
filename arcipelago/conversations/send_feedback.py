import telegram
from telegram.ext import ConversationHandler, filters, CommandHandler, MessageHandler
from arcipelago.config import chatbot_token, notification_channel
from arcipelago.conversations import text
from arcipelago.conversations import keyboards as K


(ASK_ANON, SEND_FEEDBACK, SEND_ANON) = range(3)


def feedback(update, context) -> int:
    """Asks feedback message."""
    update.message.reply_text(text.intro_feedback)
    return ASK_ANON


def ask_anon(update, context) -> int:
    """Stores feedback and asks if user wants to be anonymous."""
    context.user_data['feedback'] = update.message.text

    if update.message.from_user.username is not None:
        update.message.reply_text(text.ask_anon, reply_markup=K.yes_or_no)
        return SEND_FEEDBACK
    else:
        update.message.reply_text(text.help_no_username)
        return SEND_ANON


def send_feedback_anonymously(update, context) -> int:
    """Sends feedback message to admins channel anonymously."""
    telegram.Bot(token=chatbot_token).sendMessage(chat_id=notification_channel, text=context.user_data['feedback'])
    update.message.reply_text(text.ack_feedback_sent_anon)
    return ConversationHandler.END


def send_feedback_identified(update, context) -> int:
    """Sends feedback message to admins channel identifying the user."""
    name, username = update.message.from_user.first_name, update.message.from_user.username
    telegram.Bot(token=chatbot_token).sendMessage(chat_id=notification_channel, text=context.user_data['feedback'])
    telegram.Bot(token=chatbot_token).sendMessage(chat_id=notification_channel, text=f"Messaggio inviato da {name} (@{username}).")
    update.message.reply_text(text.ack_feedback_sent_ident)
    return ConversationHandler.END


def cancel(update, context) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text(text.ack_canceled_op)
    return ConversationHandler.END


feedback_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("feedback", feedback)],
        states = {
            ASK_ANON: [MessageHandler(filters.Filters.text & (~ filters.Filters.command), ask_anon)],
            SEND_FEEDBACK: [MessageHandler(filters.Filters.regex("Sì"), send_feedback_anonymously),
                            MessageHandler(filters.Filters.regex("No"), send_feedback_identified)],
            SEND_ANON: [MessageHandler(filters.Filters.text & (~ filters.Filters.command), send_feedback_anonymously)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
)
