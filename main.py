import logging
import os
from typing import Dict

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update, ReplyKeyboardRemove
from telegram.ext import (
    Application, CommandHandler, ContextTypes, ConversationHandler,
    MessageHandler, PicklePersistence, filters
)

# Enable logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Define command stages
SELECT_TASK, ADD_TASK, LIST_TASKS, BRAINSTORM_IDEAS, SUMMARIZE_WORK, DISCUSS_TOPIC, BACK_TO_MAIN_MENU, CHOOSE_PLAN_TASK = map(chr, range(8))
TASK_INFO, TASK_DEADLINE = map(chr, range(8, 10))
END = ConversationHandler.END  # Shortcut for ConversationHandler.END

# Define keyboards
main_menu_keyboard = ReplyKeyboardMarkup(
    [["Plan", "Control"], ["Do", "Settings"], ["Done"]],
    one_time_keyboard=True
)

plan_keyboard = ReplyKeyboardMarkup(
    [["Add Task", "List Tasks"], ["Brainstorm Ideas"], ["Back"]],
    one_time_keyboard=True
)


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Ask the user for the task they want to add."""
    await update.message.reply_text("Which task would you like to add?")
    return TASK_INFO  # Move to the next step for processing task information


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

    return CHOOSE_PLAN_TASK  # Loop back to adding another task or choose other options


async def back_to_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Transition back to the main menu."""
    await update.message.reply_text("Returning to the main menu...", reply_markup=main_menu_keyboard)
    return BACK_TO_MAIN_MENU


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
    return CHOOSE_PLAN_TASK  # Loop back to adding another task or choose other options


# Helper Functions
def facts_to_str(user_data: Dict[str, str]) -> str:
    """Format the gathered user info."""
    facts = [f"{key} - {value}" for key, value in user_data.items()]
    return "\n".join(facts).join(["\n", "\n"])

# Handler Functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Start the conversation and display the main menu."""
    reply_text = "Hi! My name is Lupin Assistant. I will help you completing your goals!"
    await update.message.reply_text(reply_text, reply_markup=main_menu_keyboard)
    return SELECT_TASK

async def plan(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Handle the 'Plan' submenu."""
    reply_text = "Plan menu: Choose an action"
    await update.message.reply_text(reply_text, reply_markup=plan_keyboard)
    return CHOOSE_PLAN_TASK

# More handler functions for different submenus...

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """End the conversation and display gathered info."""
    await update.message.reply_text(
        f"Thanks for using Lupin Assistant! We have a lot of things to do 🚀{facts_to_str(context.user_data)}Until next time!",
        reply_markup=ReplyKeyboardRemove()
    )
    return END

# Conversation Handlers
def plan_conversation() -> ConversationHandler:
    """Create a conversation handler for the 'Plan' submenu."""
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Plan$"), plan)],
        states={
            CHOOSE_PLAN_TASK: [MessageHandler(filters.Regex("^Add Task$"), add_task),
                               MessageHandler(filters.Regex("^List Tasks$"), list_tasks)
                               ],
            TASK_INFO: [MessageHandler(filters.TEXT, process_task_info)],
            # BRAINSTORM_IDEAS: [MessageHandler(filters.Regex("^Brainstorm Ideas$"), brainstorm_ideas)],
            # Add more states for other options in the 'Plan' submenu

        },
        fallbacks=[MessageHandler(filters.Regex("^Back$"), back_to_main_menu)],
        map_to_parent={
            BACK_TO_MAIN_MENU: SELECT_TASK,  # Return to top level menu
        },
        # persistent=True,
        name="plan",
    )

# Main Function
def main() -> None:
    """Run the bot."""
    load_dotenv()
    persistence = PicklePersistence(filepath="lupin_assistant")
    application = Application.builder().token(os.environ.get("TELEGRAM_TOKEN")).build()

    # Main conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_TASK: [plan_conversation(), ],
            BACK_TO_MAIN_MENU: [CommandHandler("start", start)],
        },
        fallbacks=[MessageHandler(filters.Regex("^Done$"), done)],
        name="lupin_assistant",
        # persistent=True
    )

    application.add_handler(conv_handler)

    # Additional handlers...
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
