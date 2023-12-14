from telegram.ext import ConversationHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

from conversation_handlers.plan.add_tasks.add_task_conversation_handler import add_task_conversation_handler
from conversation_handlers.plan.list_tasks.list_tasks_conversation_handler import list_tasks_conversation_handler
from conversation_handlers.plan.plan_keyboards_states import CHOOSE_PLAN_TASK, plan_keyboard
from main_keyboards_states import BACK_TO_MAIN_MENU, SELECT_TASK, main_menu_keyboard


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Transition back to the main menu."""
    await update.message.reply_text("⏎ Returning to the main menu...", reply_markup=main_menu_keyboard)
    return BACK_TO_MAIN_MENU


async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    instructions = """
📝 *Lupin Assistant \- Plan Menu*

🚀 **Add Task:** Type a task name or list multiple tasks, each on a new line\.

🔍 **List Tasks:** View all your tasks, with details on their schedule and status\.

📅 **Schedule Tasks:** Assign specific dates to your unscheduled tasks\.

💡 **Brainstorm Ideas:** Jot down and organize your thoughts or ideas related to tasks\.

_Select an option from the menu to proceed\!_
    """
    await update.message.reply_text(instructions, parse_mode='MarkdownV2', reply_markup=plan_keyboard)
    return CHOOSE_PLAN_TASK

def plan_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Plan$"), plan)],
        states={
            CHOOSE_PLAN_TASK: [add_task_conversation_handler(),
                               list_tasks_conversation_handler(),
                # MessageHandler(filters.Regex("^List Tasks$"), list_tasks_conversation_handler),
                # MessageHandler(filters.Regex("^Schedule Tasks$"), schedule_tasks_conversation_handler),
                # Add more handlers for other functionalities like Brainstorm Ideas, etc.
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_to_main_menu)],
        map_to_parent={
            BACK_TO_MAIN_MENU: SELECT_TASK  # Transition back to the main menu
        },
        name="plan"
    )
