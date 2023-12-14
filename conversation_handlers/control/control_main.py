import datetime

from telegram.ext import ConversationHandler, MessageHandler, filters
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from commands.control_commands import (
    CHOOSE_CONTROL_TASK, REVIEW_OVERDUE, REVIEW_TODAY, EDIT_TASK, DELETE_TASK, ANALYZE_CONTROL, control_keyboard
)
from main_keyboards_states import BACK_TO_MAIN_MENU, SELECT_TASK
from conversation_handlers.common_handlers import back_to_main_menu
from conversation_handlers.plan import get_next_week_date
from helpers.task_manager import categorize_tasks_by_schedule, add_date_to_history


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
    await update.message.reply_text(instructions, parse_mode='MarkdownV2', reply_markup=control_keyboard)
    return CHOOSE_CONTROL_TASK


async def review_overdue_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Show overdue tasks and provide options for each."""
    _, _, _, overdue_tasks = categorize_tasks_by_schedule(context)
    if overdue_tasks:
        context.user_data['overdue_queue'] = overdue_tasks.copy()  # Queue of overdue tasks
        return await present_overdue_task(update, context)
    else:
        await update.message.reply_text("✅ No overdue tasks.", reply_markup=control_keyboard)
        return CHOOSE_CONTROL_TASK


async def handle_overdue_task_action(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    action = update.message.text
    task_queue = context.user_data.get('overdue_queue', [])

    if not task_queue:
        await update.message.reply_text("No more overdue tasks to review.", reply_markup=control_keyboard)
        return CHOOSE_CONTROL_TASK

    current_task = task_queue[0]

    if action == "Complete":
        current_task['is_completed'] = True
        await update.message.reply_text(f"Task '{current_task['task']}' marked as complete.")
    elif action == "Reschedule for Tomorrow":
        tomorrow_date = (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        add_date_to_history(current_task, tomorrow_date)
        await update.message.reply_text(f"Task '{current_task['task']}' rescheduled for tomorrow.")
    elif action == "Reschedule for Next Week":
        next_week_date = get_next_week_date()
        add_date_to_history(current_task, next_week_date)
        await update.message.reply_text(f"Task '{current_task['task']}' rescheduled for next week.")
    elif action == "Delete Task":
        task_queue.pop(0)
        await update.message.reply_text(f"Task '{current_task['task']}' deleted.")
    elif action in ["Skip", "Stop Review"]:
        await update.message.reply_text("Review stopped. Returning to the main menu.", reply_markup=control_keyboard)
        return CHOOSE_CONTROL_TASK

    # Remove the task from the queue and proceed to the next
    task_queue.pop(0)
    if task_queue:
        await update.message.reply_text("Reviewing the next overdue task...")
        return REVIEW_OVERDUE
    else:
        await update.message.reply_text("No more overdue tasks to review.", reply_markup=control_keyboard)
        return CHOOSE_CONTROL_TASK


async def present_overdue_task(update, context: ContextTypes.DEFAULT_TYPE) -> str:
    overdue_tasks = context.user_data.get('overdue_tasks')

    if not overdue_tasks:
        await update.message.reply_text("🎉 No more overdue tasks!", reply_markup=control_keyboard)
        return CHOOSE_CONTROL_TASK

    # Present the first overdue task
    task = overdue_tasks[0]
    task_details = f"🚩 Overdue Task:\n- {task['task']}"

    # Keyboard with options for the overdue task
    task_keyboard = ReplyKeyboardMarkup(
        [["Complete", "Reschedule for Tomorrow", "Reschedule for Next Week", "Delete Task"],
         ["Skip", "Stop Review"]],
        one_time_keyboard=True
    )

    await update.message.reply_text(task_details, reply_markup=task_keyboard)
    return REVIEW_OVERDUE

async def review_today_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    pass


async def edit_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    pass


async def delete_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    pass


async def analyze_and_control(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    pass

def control_conversation() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Control$"), control)],
        states={
            CHOOSE_CONTROL_TASK: [
                MessageHandler(filters.Regex("^Review Overdue Tasks$"), review_overdue_tasks),
                MessageHandler(filters.Regex("^Review Today's Tasks$"), review_today_tasks),
                MessageHandler(filters.Regex("^Edit Tasks$"), edit_tasks),
                MessageHandler(filters.Regex("^Delete Tasks$"), delete_tasks),
                MessageHandler(filters.Regex("^Analyze & Control$"), analyze_and_control)
            ],
            REVIEW_OVERDUE: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_overdue_task_action)
            ],
            REVIEW_TODAY: [MessageHandler(filters.TEXT, review_today_tasks)],
            EDIT_TASK: [MessageHandler(filters.TEXT, edit_tasks)],
            DELETE_TASK: [MessageHandler(filters.TEXT, delete_tasks)],
            ANALYZE_CONTROL: [MessageHandler(filters.TEXT, analyze_and_control)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_to_main_menu)],
        map_to_parent={
            BACK_TO_MAIN_MENU: SELECT_TASK,  # Transition back to the main menu
        },
        name="control"
    )

