import datetime

from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ConversationHandler, MessageHandler, filters, ContextTypes

from conversation_handlers.plan.plan_keyboards_states import SCHEDULE_TASK, SCHEDULE_TASK_DATE, CUSTOM_DATE, \
    CHOOSE_PLAN_TASK, plan_keyboard, schedule_keyboard
from conversation_handlers.plan.schedule_tasks.schedule_utils import get_later_this_week_date, get_next_week_date, \
    update_task_in_list, is_valid_date


async def schedule_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Display a list of unscheduled tasks for scheduling."""
    unscheduled_tasks = [task for task in context.user_data.get('tasks', []) if not task.date_scheduled]
    if unscheduled_tasks:
        tasks_list = "\n".join([f"🔸 *{idx + 1}\.* {task.task}" for idx, task in enumerate(unscheduled_tasks)])
        instructions = """
📅 *Schedule Your Tasks*\n
Select a task number to schedule, or type 'all' to schedule each task sequentially\.
_Example:_ `1` to schedule the first task, `all` to schedule all tasks\.

_Unscheduled Tasks:_
{}
        """.format(tasks_list)
        await update.message.reply_text(instructions, parse_mode='MarkdownV2')
        return SCHEDULE_TASK
    else:
        await update.message.reply_text("👍 All tasks are currently scheduled. 📅", reply_markup=plan_keyboard)
        return CHOOSE_PLAN_TASK


async def handle_task_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle the user's task selection for scheduling."""
    user_input = update.message.text
    # Assuming 'unscheduled_tasks' is stored in context.user_data for reference
    unscheduled_tasks = [task for task in context.user_data.get('tasks', []) if not task.date_scheduled]

    if user_input.isdigit() and 0 < int(user_input) <= len(unscheduled_tasks):
        selected_task_idx = int(user_input) - 1
        # Store the selected task in context for the next step
        context.user_data['selected_task'] = unscheduled_tasks[selected_task_idx]
        await show_schedule_options(update, context)
        return SCHEDULE_TASK_DATE  # New state to handle scheduling
    elif user_input.lower() == 'all':
        # Start the process of scheduling all tasks sequentially
        if unscheduled_tasks:
            context.user_data['task_queue'] = unscheduled_tasks.copy()  # Create a queue of tasks to schedule
            return await schedule_next_task(update, context)
        else:
            await update.message.reply_text("No unscheduled tasks to schedule.", reply_markup=plan_keyboard)
            return CHOOSE_PLAN_TASK
    else:
        await update.message.reply_text("Invalid input. Please select a valid task number or type 'all'.")
        return SCHEDULE_TASK


async def schedule_next_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Schedule the next task in the queue."""
    if context.user_data.get('task_queue'):
        next_task = context.user_data['task_queue'].pop(0)
        context.user_data['selected_task'] = next_task
        await show_schedule_options(update, context)
        return SCHEDULE_TASK_DATE
    else:
        await update.message.reply_text("All tasks have been scheduled.", reply_markup=plan_keyboard)
        return CHOOSE_PLAN_TASK


async def show_schedule_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show scheduling options for the selected task."""
    await update.message.reply_text(f"Scheduling task: {context.user_data['selected_task'].task}",
                                    reply_markup=schedule_keyboard)


async def process_schedule_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Process the selected scheduling option for a task."""
    selected_option = update.message.text
    selected_task = context.user_data.get('selected_task')

    if selected_option == "Stop Scheduling":
        # Clear the task queue and stop scheduling
        context.user_data.pop('task_queue', None)
        await update.message.reply_text("⏎ Scheduling stopped. Returning to the main menu.", reply_markup=plan_keyboard)
        return CHOOSE_PLAN_TASK
    elif selected_option == "Today":
        selected_task.add_date_to_history(datetime.datetime.now())
    elif selected_option == "Later this week":
        selected_task.add_date_to_history(get_later_this_week_date())
    elif selected_option == "Tomorrow":
        selected_task.add_date_to_history(datetime.datetime.now() + datetime.timedelta(days=1))
    elif selected_option == "Next week":
        selected_task.add_date_to_history(get_next_week_date())
    elif selected_option == "Custom date":
        await update.message.reply_text("📆 Please enter a date in DD-MM-YYYY format.", reply_markup=ReplyKeyboardRemove())
        return CUSTOM_DATE  # State to handle custom date input

    # Update the task in the tasks list and check for more tasks in the queue
    update_task_in_list(context.user_data["tasks"], selected_task)
    if context.user_data.get('task_queue'):
        return await schedule_next_task(update, context)
    elif selected_option == "Skip":
        await update.message.reply_text("⏩ Task scheduling skipped.", reply_markup=plan_keyboard)
        return CHOOSE_PLAN_TASK
    else:
        await update.message.reply_text(f"🙏 Thanks for scheduling your tasks! Now it's time to work! 🤓",
                                        reply_markup=plan_keyboard)
        return CHOOSE_PLAN_TASK


async def handle_custom_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle the user's custom date input."""
    user_input = update.message.text
    selected_task = context.user_data.get('selected_task')

    # Validate and process the custom date
    if is_valid_date(user_input):
        # Convert the date from DD-MM-YYYY to a datetime.date object
        date_object = datetime.datetime.strptime(user_input, "%d-%m-%Y")

        # Add the date to the task's history and update the task in the list
        selected_task.add_date_to_history(date_object)
        update_task_in_list(context.user_data["tasks"], selected_task)
        if context.user_data.get('task_queue'):
            return await schedule_next_task(update, context)
        else:
            await update.message.reply_text(f"🙏 Thanks for scheduling your tasks! Now it's time to work! 🤓",
                                            reply_markup=plan_keyboard)
    else:
        await update.message.reply_text("Invalid date format. Please use DD-MM-YYYY format.", reply_markup=plan_keyboard)
        return CUSTOM_DATE


def schedule_tasks_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Schedule Tasks$"), schedule_tasks)],
        states={
            SCHEDULE_TASK: [MessageHandler(filters.TEXT, handle_task_selection)],
            SCHEDULE_TASK_DATE: [MessageHandler(filters.TEXT, process_schedule_option)],
            CUSTOM_DATE: [MessageHandler(filters.TEXT, handle_custom_date)],
        },
        fallbacks=[],
        map_to_parent={
            CHOOSE_PLAN_TASK: CHOOSE_PLAN_TASK,
        }
    )
