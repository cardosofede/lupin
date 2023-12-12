from telegram import Update
from telegram.ext import ContextTypes

from commands.main_commands import main_menu_keyboard, BACK_TO_MAIN_MENU


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Transition back to the main menu."""
    await update.message.reply_text("⏎ Returning to the main menu...", reply_markup=main_menu_keyboard)
    return BACK_TO_MAIN_MENU