import logging
from telegram.ext import Application, CommandHandler, MessageHandler, PicklePersistence, filters, ConversationHandler
from telegram import Update, ReplyKeyboardRemove
from telegram.ext import ContextTypes

import datetime

from config import TOKEN
from conversation_handlers.control.control_main import control_conversation
from conversation_handlers.plan.plan_main import plan_conversation
from main_keyboards_states import SELECT_TASK, END, main_menu_keyboard, BACK_TO_MAIN_MENU
from models.task import TaskStatus

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Start the conversation and display the main menu."""
    reply_text = """
👋 *Welcome to Lupin Assistant\!*
I'm here to help you manage your tasks and boost your productivity\.

🔍 *What would you like to do today?* 
Choose an option from the menu below to get started\.
    """
    await update.message.reply_text(reply_text, reply_markup=main_menu_keyboard, parse_mode='MarkdownV2')
    return SELECT_TASK


async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation and display gathered info."""
    plan_summary = get_plan_summary(context.user_data.get('tasks', []))
    do_summary = get_do_summary(context.user_data.get('tasks', []))
    control_summary = get_control_summary(context.user_data.get('tasks', []))
    tags_summary = get_tags_summary(context.user_data.get('tasks', []))

    reply_text = f"""
🚀 *Thanks for using Lupin Assistant\!*

📝 *Plan Summary*:
\- Tasks created today\: {plan_summary['today']}
\- Tasks created this week\: {plan_summary['this_week']}
\- Overdue tasks\: {plan_summary['overdue']}

🔧 *Do Summary*:
\- Incomplete tasks\: {do_summary['incomplete']}
\- Tasks completed today\: {do_summary['completed_today']}
\- Tasks completed this week\: {do_summary['completed_this_week']}

📊 *Control Summary*:
\- Total tasks\: {control_summary['total']}
\- Completion ratio\: {control_summary['completion_ratio']}%

🏷️ *Tags Summary*:
{tags_summary}

Until next time\!
    """
    await update.message.reply_text(reply_text, reply_markup=ReplyKeyboardRemove(), parse_mode='MarkdownV2')
    return END


def get_plan_summary(tasks):
    today = datetime.datetime.now().date()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    overdue_date = today - datetime.timedelta(days=1)
    summary = {"today": 0, "this_week": 0, "overdue": 0}

    for task in tasks:
        date_created = task.date_created.date()
        if date_created == today:
            summary['today'] += 1
        if start_of_week <= date_created <= today:
            summary['this_week'] += 1
        if task.date_scheduled and task.date_scheduled.date() <= overdue_date and task.status != TaskStatus.COMPLETED:
            summary['overdue'] += 1

    return summary


def get_do_summary(tasks):
    today = datetime.datetime.now().date()
    start_of_week = today - datetime.timedelta(days=today.weekday())
    do_summary = {"incomplete": 0, "completed_today": 0, "completed_this_week": 0}

    for task in tasks:
        if task.status == TaskStatus.INCOMPLETE:
            do_summary['incomplete'] += 1
        elif task.date_completed:
            date_completed = task.date_completed.date()
            if date_completed == today:
                do_summary['completed_today'] += 1
            if start_of_week <= date_completed <= today:
                do_summary['completed_this_week'] += 1

    return do_summary


def get_control_summary(tasks):
    total_tasks = len(tasks)
    completed_tasks = sum(1 for task in tasks if task.status == TaskStatus.COMPLETED)
    completion_ratio = (completed_tasks / total_tasks * 100) if total_tasks else 0
    return {"total": total_tasks, "completion_ratio": str(round(completion_ratio, 2)).replace(".", "\.")}


def get_tags_summary(tasks):
    tags_count = {}
    for task in tasks:
        for tag in task.tags:
            if tag in tags_count:
                tags_count[tag] += 1
            else:
                tags_count[tag] = 1
    tags_summary = '\n'.join([f"\- {tag}: {count}" for tag, count in tags_count.items()])
    return tags_summary if tags_summary else "No tags used\."


# Main Function
def main() -> None:
    """Run the bot."""
    persistence = PicklePersistence(filepath="lupin_assistant")
    application = Application.builder().token(TOKEN).persistence(persistence).build()

    # Main conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_TASK: [plan_conversation(),
                          control_conversation()],
            # You can add other states for different main menu items as needed
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
        name="lupin_assistant"
    )

    application.add_handler(conv_handler)
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
