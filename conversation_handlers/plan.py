from telegram.ext import ConversationHandler, MessageHandler, filters, CallbackQueryHandler
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from commands.main_commands import SELECT_TASK, main_menu_keyboard
from commands.plan_commands import CHOOSE_PLAN_TASK, TASK_INFO, SCHEDULE_TASK, BACK_TO_MAIN_MENU, plan_keyboard, \
    CUSTOM_DATE, SCHEDULE_TASK_DATE, schedule_keyboard

import datetime

from conversation_handlers.common_handlers import back_to_main_menu
from helpers.task_manager import categorize_tasks_by_schedule, format_task_summaries, add_date_to_history


async def schedule_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Display a list of unscheduled tasks for scheduling."""
    unscheduled_tasks = [task for task in context.user_data.get('tasks', []) if not task.get('date_scheduled')]
    if unscheduled_tasks:
        tasks_list = "\n".join([f"🔸 *{idx + 1}\.* {task['task']}" for idx, task in enumerate(unscheduled_tasks)])
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


async def show_schedule_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Show scheduling options for the selected task."""
    await update.message.reply_text(f"Scheduling task: {context.user_data['selected_task']['task']}", reply_markup=schedule_keyboard)


async def process_schedule_option(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Process the selected scheduling option for a task."""
    selected_option = update.message.text
    selected_task = context.user_data.get('selected_task')

    if selected_option == "Stop Scheduling":
        # Clear the task queue and stop scheduling
        context.user_data.pop('task_queue', None)
        await update.message.reply_text("Scheduling stopped. Returning to the main menu.", reply_markup=plan_keyboard)
        return CHOOSE_PLAN_TASK
    elif selected_option == "Today":
        add_date_to_history(selected_task, datetime.datetime.now().strftime("%Y-%m-%d"))
    elif selected_option == "Later this week":
        add_date_to_history(selected_task, get_later_this_week_date())
    elif selected_option == "Tomorrow":
        add_date_to_history(selected_task, (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d"))
    elif selected_option == "Next week":
        add_date_to_history(selected_task, get_next_week_date())
    elif selected_option == "Custom date":
        await update.message.reply_text("Please enter a date in YYYY-MM-DD format.", reply_markup=ReplyKeyboardRemove())
        return CUSTOM_DATE  # State to handle custom date input

    # Update the task in the tasks list and check for more tasks in the queue
    update_task_in_list(context.user_data["tasks"], selected_task)
    if context.user_data.get('task_queue'):
        return await schedule_next_task(update, context)
    elif selected_option == "Skip":
        await update.message.reply_text("Task scheduling skipped.", reply_markup=plan_keyboard)
        return CHOOSE_PLAN_TASK
    else:
        await update.message.reply_text(f"Task '{selected_task['task']}' scheduled for {selected_task['date_scheduled']}.", reply_markup=plan_keyboard)
        return CHOOSE_PLAN_TASK


def get_later_this_week_date():
    """Calculate a date later this week."""
    today = datetime.datetime.now().date()
    days_to_weekend = 6 - today.weekday()  # Days until Sunday
    later_this_week = today + datetime.timedelta(days=min(2, days_to_weekend))  # Assuming "later this week" means in the next 2 days or until Sunday
    return later_this_week.strftime("%Y-%m-%d")


def get_next_week_date():
    """Calculate a date for next week."""
    today = datetime.datetime.now().date()
    next_week = today + datetime.timedelta(days=7 - today.weekday())  # Start of next week (Monday)
    return next_week.strftime("%Y-%m-%d")


def update_task_in_list(tasks, updated_task):
    """Update a task in the tasks list."""
    for task in tasks:
        if task['task'] == updated_task['task'] and task['date_created'] == updated_task['date_created']:
            task.update(updated_task)
            break


async def handle_custom_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle the user's custom date input."""
    user_input = update.message.text
    selected_task = context.user_data.get('selected_task')

    # Validate and process the custom date
    if is_valid_date(user_input):
        add_date_to_history(selected_task, user_input)
        # Update the task in the tasks list
        update_task_in_list(context.user_data["tasks"], selected_task)

        await update.message.reply_text(f"Task '{selected_task['task']}' scheduled for {user_input}.", reply_markup=plan_keyboard)
        return CHOOSE_PLAN_TASK
    else:
        await update.message.reply_text("Invalid date format. Please use YYYY-MM-DD format.", reply_markup=plan_keyboard)
        return CUSTOM_DATE

def is_valid_date(date_str):
    """Check if the provided string is a valid date in YYYY-MM-DD format."""
    try:
        datetime.datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except ValueError:
        return False


async def handle_task_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle the user's task selection for scheduling."""
    user_input = update.message.text
    # Assuming 'unscheduled_tasks' is stored in context.user_data for reference
    unscheduled_tasks = [task for task in context.user_data.get('tasks', []) if not task.get('date_scheduled')]

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


async def process_task_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Store the provided task info and confirm."""
    user_input = update.message.text

    # Determine input type and process accordingly
    if any(symbol in user_input for symbol in ["-", "*", ".", "\n"]):
        # Multiple tasks with separators
        tasks = parse_multiple_tasks(user_input)
    else:
        # Single task name
        tasks = [create_simple_task(user_input)]

    # Ensure 'tasks' key in user_data is a list
    if 'tasks' not in context.user_data:
        context.user_data['tasks'] = []

    context.user_data['tasks'].extend(tasks)

    # Format confirmation message
    task_list_formatted = "\n".join([f"✅ {task['task']}" for task in tasks])
    confirmation_message = f"""
📝 You have successfully added the following task(s):

{task_list_formatted}

🤔 What would you like to do next?
    """
    await update.message.reply_text(confirmation_message, reply_markup=plan_keyboard)
    return CHOOSE_PLAN_TASK


def parse_multiple_tasks(user_input):
    """Parse multiple tasks from user input."""
    task_lines = [line.strip("-*. ") for line in user_input.split('\n') if line.strip("-*. ")]
    return [create_simple_task(task) for task in task_lines]


def parse_full_task_input(user_input):
    """Parse a single task with full details from user input."""
    lines = user_input.split('\n')
    task_details = {
        "task": lines[0].strip(),
        "description": lines[1].strip() if len(lines) > 1 else "",
        "date_created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tags": extract_tags(lines[2]) if len(lines) > 2 else [],
        "date_scheduled": lines[3].strip() if len(lines) > 3 else "",
        "priority": lines[4].strip() if len(lines) > 4 else "",
        "is_completed": False,
    }
    return task_details


def create_simple_task(task_name):
    """Create a task dictionary from a simple task name."""
    return {
        "task": task_name,
        "description": "",
        "date_created": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "tags": [],
        "date_scheduled": "",
        "priority": "",
        "is_completed": False,
    }


def extract_tags(tag_line):
    """Extract tags from a line of text."""
    return [tag.strip() for tag in tag_line.split(',')]


async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle the 'Plan' submenu."""
    instructions = """
📝 *Lupin Assistant \- Plan Menu*

🚀 **Add Task:** Type a task name or list multiple tasks, each on a new line\. 

🔍 **List Tasks:** View all your tasks, with details on their schedule and status\.

📅 **Schedule Tasks:** Assign specific dates to your unscheduled tasks for better organization\.

💡 **Brainstorm Ideas:** Jot down and organize your thoughts or ideas related to tasks\.

_Select an option from the menu to proceed\!_
    """
    await update.message.reply_text(instructions, parse_mode='MarkdownV2', reply_markup=plan_keyboard)
    return CHOOSE_PLAN_TASK


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Ask the user for the task(s) they want to add."""
    instructions = """
🚀 **Add Your Task\(s\)**
You can add tasks in different formats:

1️⃣ **Single Task:** Just type the task name
_Example:_
`Buy groceries`

2️⃣ **Multiple Tasks:** Start each task on a new line\. Optional you can start with [`\-`, `*`, `\.`]
_Example:_
Buy groceries
Call the electrician
Schedule a meeting

🔍 Choose your format and send your task\(s\)\!
 """
    await update.message.reply_text(instructions, parse_mode='MarkdownV2')
    return TASK_INFO


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """List the tasks added so far."""
    if 'tasks' not in context.user_data or not context.user_data['tasks']:
        await update.message.reply_text("You haven't added any tasks yet. 🤔 What would you like to do next?",
                                        reply_markup=plan_keyboard)
    else:
        not_scheduled, scheduled_today, scheduled_week, overdue = categorize_tasks_by_schedule(context)
        message = f"""
📋 *Current Tasks Summary*:

📌 *Not Scheduled:*
{format_task_summaries(not_scheduled)}

📅 *Scheduled for Today:*
{format_task_summaries(scheduled_today)}

🗓️ *Scheduled This Week:*
{format_task_summaries(scheduled_week)}

⏰ *Overdue Tasks:*
{format_task_summaries(overdue)}

🤔 *What would you like to do next?*
        """
        await update.message.reply_text(message, reply_markup=plan_keyboard, parse_mode='MarkdownV2')
    return CHOOSE_PLAN_TASK


def plan_conversation() -> ConversationHandler:
    """Create a conversation handler for the 'Plan' submenu."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Plan$"), plan)],
        states={
            CHOOSE_PLAN_TASK: [MessageHandler(filters.Regex("^Add Task$"), add_task),
                               MessageHandler(filters.Regex("^List Tasks$"), list_tasks),
                               MessageHandler(filters.Regex("^Schedule Tasks$"), schedule_tasks)],
            TASK_INFO: [MessageHandler(filters.TEXT & ~filters.Regex("^Back$"), process_task_info)],
            SCHEDULE_TASK: [MessageHandler(filters.TEXT, handle_task_selection)],
            SCHEDULE_TASK_DATE: [MessageHandler(filters.TEXT, process_schedule_option)],
            CUSTOM_DATE: [MessageHandler(filters.TEXT, handle_custom_date)],
            # Implement this function to handle custom date input
        },
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_to_main_menu)],
        map_to_parent={
            BACK_TO_MAIN_MENU: SELECT_TASK,  # Transition back to the main menu
        },
        name="plan"
    )
