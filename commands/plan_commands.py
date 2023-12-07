from telegram import ReplyKeyboardMarkup

# Define command stages for the 'Plan' conversation
CHOOSE_PLAN_TASK, TASK_INFO, BACK_TO_MAIN_MENU = map(chr, range(3))

# Define keyboards for the 'Plan' conversation
plan_keyboard = ReplyKeyboardMarkup(
    [["Add Task", "List Tasks"], ["Brainstorm Ideas"], ["Back"]],
    one_time_keyboard=True
)
