from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from conversation_handlers.plan.plan_keyboards_states import (
    CHOOSE_PLAN_TASK,
    plan_keyboard,
)
from models.task import Task


# Function to handle listing tasks
async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    if "tasks" not in context.user_data or not context.user_data["tasks"]:
        await update.message.reply_text(
            "You haven't added any tasks yet. 🤔 What would you like to do next?",
            reply_markup=plan_keyboard,
        )
    else:
        (
            not_scheduled,
            scheduled_today,
            scheduled_week,
            overdue,
        ) = Task.categorize_tasks_by_schedule(context.user_data["tasks"])
        message = f"""
📋 *Current Tasks Summary*:

📌 *Not Scheduled:*
{Task.format_task_summaries(not_scheduled)}

📅 *Scheduled for Today:*
{Task.format_task_summaries(scheduled_today)}

🗓️ *Scheduled This Week:*
{Task.format_task_summaries(scheduled_week)}

⏰ *Overdue Tasks:*
{Task.format_task_summaries(overdue)}

🤔 *What would you like to do next?*
        """
        await update.message.reply_text(
            message, reply_markup=plan_keyboard, parse_mode="MarkdownV2"
        )
    return CHOOSE_PLAN_TASK


def list_tasks_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^List Tasks$"), list_tasks)],
        states={
            # You can add more states here if you plan to expand the functionality of list tasks
        },
        fallbacks=[],
        map_to_parent={
            CHOOSE_PLAN_TASK: CHOOSE_PLAN_TASK  # Transition back to the CHOOSE_PLAN_TASK state
        },
    )
