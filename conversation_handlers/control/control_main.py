from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from conversation_handlers.common_handlers import back_to_main_menu
from conversation_handlers.control.control_keyboards_states import (
    CHOOSE_CONTROL_TASK,
    control_keyboard,
)
from conversation_handlers.control.review_overdue_tasks.review_overdue_tasks_conversation_handler import (
    review_overdue_tasks_conversation_handler,
)
from conversation_handlers.control.review_today_tasks.review_today_tasks_conversation_handler import (
    review_today_tasks_conversation_handler,
)
from main_keyboards_states import BACK_TO_MAIN_MENU, SELECT_TASK


async def control(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle the 'Control' submenu."""
    instructions = """
🛠️ *Lupin Assistant \- Control Menu*

🔎 **Review Overdue Tasks:** Manage and update your overdue tasks\.

📆 **Review Today's Tasks:** Look at tasks scheduled for today and update them as needed\.

✏️ **Edit Tasks:** Modify details of your existing tasks\.

🗑️ **Delete Tasks:** Remove tasks that are no longer needed\.

🧠 **Analyze & Control:** Get insights and control your tasks with the help of AI\.

_Select an option from the menu to proceed\!_
    """
    await update.message.reply_text(
        instructions, parse_mode="MarkdownV2", reply_markup=control_keyboard
    )
    return CHOOSE_CONTROL_TASK


def control_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Control$"), control)],
        states={
            CHOOSE_CONTROL_TASK: [
                review_overdue_tasks_conversation_handler(),
                review_today_tasks_conversation_handler(),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_to_main_menu)],
        map_to_parent={
            BACK_TO_MAIN_MENU: SELECT_TASK,  # Transition back to the main menu
        },
        name="control",
    )
