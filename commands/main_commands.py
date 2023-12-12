from telegram import ReplyKeyboardMarkup
from telegram.ext import ConversationHandler

# Define command stages
SELECT_TASK, BACK_TO_MAIN_MENU = map(chr, range(2))
END = ConversationHandler.END  # Shortcut for ConversationHandler.END

# Define keyboards
main_menu_keyboard = ReplyKeyboardMarkup(
    [["Plan", "Do"], ["Control", "Settings"], ["Done"]],
    one_time_keyboard=True
)