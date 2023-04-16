import telegram
from telegram.ext import ConversationHandler, filters, CommandHandler
from arcipelago.config import chatbot_token, notification_channel
from arcipelago.conversations import text


def feedback(update, context) -> int:
    """Sends feedback message to admins group."""
    if update.message.text.strip() == "/feedback":
        update.message.reply_text(text.help_feedback)
    else:
        telegram.Bot(token=chatbot_token).sendMessage(chat_id=notification_channel, text=update.message.text[10:])
        update.message.reply_text(text.ack_feedback_received)
    return ConversationHandler.END


def cancel(update, context) -> int:
    """Cancels and ends the conversation."""
    update.message.reply_text(text.ack_canceled_op)
    return ConversationHandler.END


feedback_conv_handler = ConversationHandler(
        entry_points=[CommandHandler("feedback", feedback)],
        fallbacks=[CommandHandler("cancel", cancel)],
)
