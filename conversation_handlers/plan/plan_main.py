from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from conversation_handlers.common_handlers import back_to_main_menu
from conversation_handlers.plan.add_tasks.add_task_conversation_handler import (
    add_task_conversation_handler,
)
from conversation_handlers.plan.list_tasks.list_tasks_conversation_handler import (
    list_tasks_conversation_handler,
)
from conversation_handlers.plan.plan_keyboards_states import (
    CHOOSE_PLAN_TASK,
    plan_keyboard,
)
from conversation_handlers.plan.schedule_tasks.schedule_tasks_conversation_handler import (
    schedule_tasks_conversation_handler,
)
from main_keyboards_states import BACK_TO_MAIN_MENU, SELECT_TASK


async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    instructions = """
📝 *Lupin Assistant \- Plan Menu*

🚀 **Add Task:** Type a task name or list multiple tasks, each on a new line\.

🔍 **List Tasks:** View all your tasks, with details on their schedule and status\.

📅 **Schedule Tasks:** Assign specific dates to your unscheduled tasks\.

💡 **Brainstorm Ideas:** Jot down and organize your thoughts or ideas related to tasks\.

_Select an option from the menu to proceed\!_
    """
    await update.message.reply_text(
        instructions, parse_mode="MarkdownV2", reply_markup=plan_keyboard
    )
    return CHOOSE_PLAN_TASK


def plan_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Plan$"), plan)],
        states={
            CHOOSE_PLAN_TASK: [
                add_task_conversation_handler(),
                list_tasks_conversation_handler(),
                schedule_tasks_conversation_handler(),
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_to_main_menu)],
        map_to_parent={
            BACK_TO_MAIN_MENU: SELECT_TASK  # Transition back to the main menu
        },
        name="plan",
    )
