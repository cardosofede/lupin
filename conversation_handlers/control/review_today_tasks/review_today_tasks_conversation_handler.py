import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, filters

from conversation_handlers.common_handlers import back_to_main_menu
from conversation_handlers.control.control_keyboards_states import (
    CHOOSE_CONTROL_TASK,
    REVIEW_TODAY,
    SELECT_TODAY_TASK,
    control_keyboard,
    review_overdue_keyboard,
)
from conversation_handlers.plan.schedule_tasks.schedule_utils import (
    get_next_week_date,
    remove_task_from_list,
    update_task_in_list,
)
from models.task import Task, TaskStatus


async def handle_scheduled_today_task_action(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Handle actions on scheduled_today tasks."""
    current_task = context.user_data["selected_scheduled_today_task"]
    action = update.message.text
    # Process the action on the current task
    # TODO: Abstract this behaviour since it's duplicated in review_overdue_tasks_conversation_handler.py
    if action == "Complete":
        current_task.status = TaskStatus.COMPLETED
        current_task.date_completed = datetime.datetime.now()
        await update.message.reply_text(
            f"✅ Task '{current_task.task}' marked as complete."
        )
    elif action == "Reschedule for Tomorrow":
        tomorrow_date = datetime.datetime.now() + datetime.timedelta(days=1)
        current_task.add_date_to_history(tomorrow_date)
        current_task.status = TaskStatus.INCOMPLETE
        await update.message.reply_text(
            f"🗓️ Task '{current_task.task}' rescheduled for tomorrow."
        )
    elif action == "Reschedule for Next Week":
        next_week_date = get_next_week_date()
        current_task.add_date_to_history(next_week_date)
        current_task.status = TaskStatus.INCOMPLETE
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


async def present_scheduled_today_task(
    update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    scheduled_today = context.user_data.get("scheduled_today")
    if not scheduled_today:
        await update.message.reply_text(
            "🎉 No more today tasks!", reply_markup=control_keyboard
        )
        return CHOOSE_CONTROL_TASK

    # Present a list of today tasks
    tasks_list = "\n".join(
        [
            f"{'🔻' if task.status == TaskStatus.INCOMPLETE else '✅'} *{idx + 1}\.* {task.task}"
            for idx, task in enumerate(scheduled_today)
        ]
    )
    instructions = """
🔔 *Review Today's Tasks*\n
Select a task number to review, or type 'all' to review each task sequentially\.
_Example:_ `1` to review the first task, `all` to review all tasks\.

_Today's Tasks:_
{}
    """.format(
        tasks_list
    )
    await update.message.reply_text(instructions, parse_mode="MarkdownV2")
    return SELECT_TODAY_TASK


async def review_scheduled_today_tasks(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> str:
    """Show today tasks and provide options for each."""
    _, scheduled_today, _, _ = Task.categorize_tasks_by_schedule(
        context.user_data.get("tasks", [])
    )
    if scheduled_today:
        context.user_data[
            "scheduled_today"
        ] = scheduled_today.copy()  # Store overdue tasks in context
        return await present_scheduled_today_task(update, context)
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
    scheduled_today = context.user_data.get("scheduled_today", [])

    if user_input.isdigit() and 0 < int(user_input) <= len(scheduled_today):
        selected_task_idx = int(user_input) - 1
        selected_task = scheduled_today[selected_task_idx]
        context.user_data["task_queue"] = [
            selected_task
        ]  # Queue with the selected task
        return await show_task_actions(update, context)
    elif user_input.lower() == "all":
        context.user_data[
            "task_queue"
        ] = scheduled_today.copy()  # Queue of all overdue tasks
        return await show_task_actions(update, context)
    else:
        await update.message.reply_text(
            "‼️ Invalid input. Please select a valid task number or type 'all'."
        )
        return SELECT_TODAY_TASK


async def show_task_actions(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show scheduling options for the selected task."""
    task_queue = context.user_data.get("task_queue", [])

    if len(task_queue) == 0:
        await update.message.reply_text(
            "🙌 No more tasks for today to review.", reply_markup=control_keyboard
        )
        return CHOOSE_CONTROL_TASK
    else:
        task = task_queue.pop(0)
        context.user_data["selected_scheduled_today_task"] = task
        await update.message.reply_text(
            f"🗓️ Control task: {task.task}", reply_markup=review_overdue_keyboard
        )
        return REVIEW_TODAY


def review_today_tasks_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[
            MessageHandler(
                filters.Regex("^Review Today's Tasks$"), review_scheduled_today_tasks
            )
        ],
        states={
            SELECT_TODAY_TASK: [MessageHandler(filters.TEXT, handle_task_selection)],
            REVIEW_TODAY: [
                MessageHandler(filters.TEXT, handle_scheduled_today_task_action)
            ],
        },
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_to_main_menu)],
        map_to_parent={
            CHOOSE_CONTROL_TASK: CHOOSE_CONTROL_TASK  # Transition back to the main menu
        },
    )
