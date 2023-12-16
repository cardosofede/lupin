import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from conversation_handlers.common_handlers import back_to_main_menu
from conversation_handlers.control.control_keyboards_states import (
    CHOOSE_CONTROL_TASK,
    REVIEW_OVERDUE,
    SELECT_OVERDUE_TASK,
    control_keyboard,
    review_overdue_keyboard,
)
from conversation_handlers.plan.schedule_tasks.schedule_utils import (
    get_next_week_date,
    remove_task_from_list,
    update_task_in_list,
)
from models.task import Task, TaskStatus


async def handle_overdue_task_action(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Handle actions on overdue tasks."""
    current_task = context.user_data["selected_overdue_task"]
    action = update.message.text
    # Process the action on the current task
    if action == "Complete":
        current_task.status = TaskStatus.COMPLETED
        current_task.date_completed = datetime.datetime.now()
        await update.message.reply_text(
            f"✅ Task '{current_task.task}' marked as complete."
        )
    elif action == "Reschedule for Tomorrow":
        tomorrow_date = datetime.datetime.now() + datetime.timedelta(days=1)
        current_task.add_date_to_history(tomorrow_date)
        await update.message.reply_text(
            f"🗓️ Task '{current_task.task}' rescheduled for tomorrow."
        )
    elif action == "Reschedule for Next Week":
        next_week_date = get_next_week_date()
        current_task.add_date_to_history(next_week_date)
        await update.message.reply_text(
            f"📅 Task '{current_task.task}' rescheduled for next week."
        )
    elif action == "Delete Task":
        await update.message.reply_text(f"🗑️ Task '{current_task.task}' deleted.")
    elif action == "Skip":
        await update.message.reply_text("⏭️ Task skipped.")
    elif action == "Stop Review":
        await update.message.reply_text(
            "✋ Review stopped. Returning to the main menu.",
            reply_markup=control_keyboard,
        )
        return CHOOSE_CONTROL_TASK

    # Update the task list in context
    if action == "Delete Task":
        remove_task_from_list(context.user_data["tasks"], current_task)
    else:
        update_task_in_list(context.user_data["tasks"], current_task)
    task_queue = context.user_data.get("task_queue", [])
    # Process the next task in the queue if any
    if task_queue:
        return await show_task_actions(update, context)
    else:
        await update.message.reply_text(
            "🍾 All tasks have been reviewed.", reply_markup=control_keyboard
        )
        return CHOOSE_CONTROL_TASK


async def present_overdue_task(update, context: ContextTypes.DEFAULT_TYPE) -> str:
    overdue_tasks = context.user_data.get("overdue_tasks")
    if not overdue_tasks:
        await update.message.reply_text(
            "🎉 No more overdue tasks!", reply_markup=control_keyboard
        )
        return CHOOSE_CONTROL_TASK

    # Present a list of overdue tasks
    tasks_list = "\n".join(
        [f"🚩 *{idx + 1}\.* {task.task}" for idx, task in enumerate(overdue_tasks)]
    )
    instructions = """
🔔 *Review Overdue Tasks*\n
Select a task number to review, or type 'all' to review each task sequentially\.
_Example:_ `1` to review the first task, `all` to review all tasks\.

_Overdue Tasks:_
{}
    """.format(
        tasks_list
    )
    await update.message.reply_text(instructions, parse_mode="MarkdownV2")
    return SELECT_OVERDUE_TASK


async def review_overdue_tasks(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Show overdue tasks and provide options for each."""
    _, _, _, overdue_tasks = Task.categorize_tasks_by_schedule(
        context.user_data.get("tasks", [])
    )
    if overdue_tasks:
        context.user_data[
            "overdue_tasks"
        ] = overdue_tasks.copy()  # Store overdue tasks in context
        return await present_overdue_task(update, context)
    else:
        await update.message.reply_text(
            "✅ No overdue tasks.", reply_markup=control_keyboard
        )
        return CHOOSE_CONTROL_TASK


async def handle_task_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Handle the user's task selection for overdue tasks."""
    user_input = update.message.text.strip()
    overdue_tasks = context.user_data.get("overdue_tasks", [])

    if user_input.isdigit() and 0 < int(user_input) <= len(overdue_tasks):
        selected_task_idx = int(user_input) - 1
        selected_task = overdue_tasks[selected_task_idx]
        context.user_data["task_queue"] = [
            selected_task
        ]  # Queue with the selected task
        return await show_task_actions(update, context)
    elif user_input.lower() == "all":
        context.user_data[
            "task_queue"
        ] = overdue_tasks.copy()  # Queue of all overdue tasks
        return await show_task_actions(update, context)
    else:
        await update.message.reply_text(
            "Invalid input. Please select a valid task number or type 'all'."
        )
        return SELECT_OVERDUE_TASK


async def show_task_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show scheduling options for the selected task."""
    task_queue = context.user_data.get("task_queue", [])

    if len(task_queue) == 0:
        await update.message.reply_text(
            "🍾 No more overdue tasks to review.", reply_markup=control_keyboard
        )
        return CHOOSE_CONTROL_TASK
    else:
        task = task_queue.pop(0)
        context.user_data["selected_overdue_task"] = task
        await update.message.reply_text(
            f"🗓️ Scheduling task: {task.task}", reply_markup=review_overdue_keyboard
        )
        return REVIEW_OVERDUE


def review_overdue_tasks_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^Review Overdue Tasks$"), review_overdue_tasks
            )
        ],
        states={
            SELECT_OVERDUE_TASK: [MessageHandler(filters.TEXT, handle_task_selection)],
            REVIEW_OVERDUE: [MessageHandler(filters.TEXT, handle_overdue_task_action)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_to_main_menu)],
        map_to_parent={
            CHOOSE_CONTROL_TASK: CHOOSE_CONTROL_TASK  # Transition back to the main menu
        },
    )
