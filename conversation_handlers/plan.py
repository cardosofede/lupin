from telegram.ext import ConversationHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes

from commands.control_commands import SELECT_TASK, main_menu_keyboard
from commands.plan_commands import CHOOSE_PLAN_TASK, TASK_INFO, BACK_TO_MAIN_MENU, plan_keyboard

async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle the 'Plan' submenu."""
    reply_text = "Plan menu: Choose an action"
    await update.message.reply_text(reply_text, reply_markup=plan_keyboard)
    return CHOOSE_PLAN_TASK


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Ask the user for the task they want to add."""
    await update.message.reply_text("Which task would you like to add?")
    return TASK_INFO


async def process_task_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Store the provided task info and confirm."""
    user_task = update.message.text

    # Ensure there's a 'tasks' key in user_data and it's a list
    if 'tasks' not in context.user_data:
        context.user_data['tasks'] = []

    # Add the new task to the 'tasks' list
    context.user_data['tasks'].append(user_task)

    await update.message.reply_text(f"Task '{user_task}' added successfully. What would you like to do next?",
                                    reply_markup=plan_keyboard)
    return CHOOSE_PLAN_TASK


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """List the tasks added so far."""
    end_message = "What would you like to do next?"
    if 'tasks' not in context.user_data or not context.user_data['tasks']:
        await update.message.reply_text(f"You haven't added any tasks yet. {end_message}",
                                        reply_markup=plan_keyboard)
    else:
        tasks = "\n".join(context.user_data['tasks'])
        await update.message.reply_text(f"You've added the following tasks:\n{tasks}\n{end_message}",
                                        reply_markup=plan_keyboard)
    return CHOOSE_PLAN_TASK


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
            TASK_INFO: [MessageHandler(filters.TEXT, process_task_info)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_to_main_menu)],
        map_to_parent={
            BACK_TO_MAIN_MENU: SELECT_TASK,  # Transition back to the main menu
        },
        name="plan"
    )
