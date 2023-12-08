from telegram.ext import ConversationHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

from commands.control_commands import SELECT_TASK, main_menu_keyboard
from commands.plan_commands import CHOOSE_PLAN_TASK, TASK_INFO, BACK_TO_MAIN_MENU, plan_keyboard

import datetime


async def process_task_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Store the provided task info and confirm."""
    user_input = update.message.text

    # Determine input type and process accordingly
    if any(symbol in user_input for symbol in ["-", "*", "."]):
        # Multiple tasks with separators
        tasks = parse_multiple_tasks(user_input)
    elif "\n" in user_input:
        # Single task with full details
        tasks = [parse_full_task_input(user_input)]
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

"🤔 What would you like to do next?"
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
    reply_text = """
📝 *Plan Menu*

In the Plan section, you can:

1️⃣ **Add Tasks** 
   \- Quickly add a single task or multiple tasks\.
   \- Provide detailed task information including description, tags, and deadlines\.

2️⃣ **List Tasks** 
   \- View all your planned tasks\.
   \- Get a summary of tasks by date, priority, or tags\.

Choose an action from the menu below to get started\!
    """
    await update.message.reply_text(reply_text, reply_markup=plan_keyboard, parse_mode='MarkdownV2')
    return CHOOSE_PLAN_TASK



async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Ask the user for the task(s) they want to add."""
    instructions = """
🚀 **Add Your Task\(s\)**
You can add tasks in different formats:

1️⃣ **Single Simple Task**
   Just type the task name
   _Example:_
   `Buy groceries`

2️⃣ **Multiple Simple Tasks**
   Start each task on a new line with `[\-, *, .]`
   _Example:_
        \- Buy groceries
        \- Call the electrician
        \- Schedule a meeting

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
        now = datetime.datetime.now()
        today = now.date()
        end_of_week = today + datetime.timedelta(days=6 - today.weekday())

        not_scheduled, scheduled_today, scheduled_week, overdue = categorize_tasks_by_schedule(context.user_data['tasks'], today, end_of_week)

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


def categorize_tasks_by_schedule(tasks, today, end_of_week):
    not_scheduled, scheduled_today, scheduled_week, overdue = [], [], [], []
    for task in tasks:
        date_scheduled = task.get('date_scheduled')
        if date_scheduled:
            date_scheduled = datetime.datetime.strptime(date_scheduled, "%Y-%m-%d").date()
            if date_scheduled < today:
                overdue.append(task)
            elif date_scheduled == today:
                scheduled_today.append(task)
            elif today < date_scheduled <= end_of_week:
                scheduled_week.append(task)
        else:
            not_scheduled.append(task)
    return not_scheduled, scheduled_today, scheduled_week, overdue


def format_task_summaries(tasks):
    """Format task summaries for display."""
    summaries = []
    for task in tasks:
        summary = f"🔹 *{task['task']}*"
        # if task.get('description'):
        #     summary += f" - _{task['description']}_"
        # if task.get('date_scheduled'):
        #     summary += f" 📅 {task['date_scheduled']}"
        # if task.get('priority'):
        #     summary += f" 🔺 {task['priority']}"
        summaries.append(summary)
    return "\n".join(summaries)



async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Transition back to the main menu."""
    await update.message.reply_text("Returning to the main menu...", reply_markup=main_menu_keyboard)
    return BACK_TO_MAIN_MENU


def plan_conversation() -> ConversationHandler:
    """Create a conversation handler for the 'Plan' submenu."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Plan$"), plan)],
        states={
            CHOOSE_PLAN_TASK: [MessageHandler(filters.Regex("^Add Task$"), add_task),
                               MessageHandler(filters.Regex("^List Tasks$"), list_tasks)],
            TASK_INFO: [MessageHandler(filters.TEXT & ~filters.Regex("^Back$"), process_task_info)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_to_main_menu)],
        map_to_parent={
            BACK_TO_MAIN_MENU: SELECT_TASK,  # Transition back to the main menu
        },
        name="plan"
    )
