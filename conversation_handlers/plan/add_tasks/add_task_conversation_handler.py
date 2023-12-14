from telegram.ext import ConversationHandler, MessageHandler, filters
from telegram import Update
from telegram.ext import ContextTypes
from conversation_handlers.plan.plan_keyboards_states import CHOOSE_PLAN_TASK, TASK_INFO, plan_keyboard
from models import Task


# Function to start the add task conversation
async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    instructions = """
🚀 **Add Your Task\(s\)**
You can add tasks in different formats:

1️⃣ **Single Task:** Just type the task name
_Example:_ `Buy groceries`

2️⃣ **Multiple Tasks:** Start each task on a new line\. Optional you can start with [\-, \*, \.]
_Example:_ 
Buy groceries
Call the electrician
Schedule a meeting

🔍 Choose your format and send your task\(s\)\!
    """
    await update.message.reply_text(instructions, parse_mode='MarkdownV2')
    return TASK_INFO


# Function to process task info
async def process_task_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    user_input = update.message.text

    # Determine input type and process accordingly
    if any(symbol in user_input for symbol in ["-", "*", ".", "\n"]):
        tasks = Task.create_multiple_tasks(user_input.strip())
    else:
        tasks = [Task.create_simple_task(user_input.strip())]

    # Ensure 'tasks' key in user_data is a list
    if 'tasks' not in context.user_data:
        context.user_data['tasks'] = []

    context.user_data['tasks'].extend(tasks)

    # Format confirmation message
    task_list_formatted = "\n".join([f"✅ {task.task}" for task in tasks])  # Accessing the 'task' attribute of Task instances
    confirmation_message = f"📝 You have successfully added the following task(s):\n{task_list_formatted}"
    await update.message.reply_text(confirmation_message, reply_markup=plan_keyboard)
    return CHOOSE_PLAN_TASK


def add_task_conversation_handler() -> ConversationHandler:
    return ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^Add Task$"), add_task)],
        states={
            TASK_INFO: [MessageHandler(filters.TEXT & ~filters.COMMAND, process_task_info)]
        },
        fallbacks=[],
        map_to_parent={
            CHOOSE_PLAN_TASK: CHOOSE_PLAN_TASK
        }
    )
