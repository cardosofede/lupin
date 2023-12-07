import logging
from telegram.ext import Application, CommandHandler, MessageHandler, PicklePersistence, filters, ConversationHandler
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

from conversation_handlers.plan import plan_conversation
from helpers.utils import facts_to_str
from config import TOKEN
from commands.control_commands import SELECT_TASK, END, main_menu_keyboard


# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Start the conversation and display the main menu."""
    reply_text = "Hi! My name is Lupin Assistant. I will help you completing your goals!"
    await update.message.reply_text(reply_text, reply_markup=main_menu_keyboard)
    return SELECT_TASK


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation and display gathered info."""
    await update.message.reply_text(
        f"Thanks for using Lupin Assistant! We have a lot of things to do 🚀{facts_to_str(context.user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove()
    )
    return END

# Main Function
def main() -> None:
    """Run the bot."""
    persistence = PicklePersistence(filepath="lupin_assistant")
    application = Application.builder().token(TOKEN).persistence(persistence).build()

    # Main conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_TASK: [plan_conversation()],
            # You can add other states for different main menu items as needed
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
        name="lupin_assistant"
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
