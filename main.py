import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# Apnar details
BOT_TOKEN = "8170872541:AAEW9FehHQ7RoDaTIGuWywH4xubLaALcZd8"

# Logging setup (ki hochche ta dekhar jonno)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def delete_service_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Jekono service message (User add, VC start) delete korbe."""
    try:
        await context.bot.delete_message(
            chat_id=update.effective_chat.id,
            message_id=update.message.message_id
        )
        print(f"Deleted a service message in: {update.effective_chat.id}")
    except Exception as e:
        print(f"Error deleting message: {e}")

if __name__ == '__main__':
    # Application build kora
    application = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Filter: New members, Left members, VC start/end/invite
    service_message_filter = (
        filters.StatusUpdate.NEW_CHAT_MEMBERS |
        filters.StatusUpdate.LEFT_CHAT_MEMBER |
        filters.StatusUpdate.VIDEO_CHAT_STARTED |
        filters.StatusUpdate.VIDEO_CHAT_ENDED |
        filters.StatusUpdate.VIDEO_CHAT_INVITE |
        filters.StatusUpdate.VIDEO_CHAT_SCHEDULED
    )

    # Handler add kora
    delete_handler = MessageHandler(service_message_filter, delete_service_messages)
    application.add_handler(delete_handler)

    print("Bot is running...")
    application.run_polling()
