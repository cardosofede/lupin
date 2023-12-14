from telegram import ReplyKeyboardMarkup

# Define command stages for the 'Plan' conversation
CHOOSE_PLAN_TASK, SCHEDULE_TASK, CUSTOM_DATE, SCHEDULE_TASK_DATE = map(chr, range(4))

# Define command stages for the 'Add Task' conversation
TASK_INFO, ADD_TASK = map(chr, range(5, 7))

# Define keyboards for the 'Plan' conversation
plan_keyboard = ReplyKeyboardMarkup(
    [["Add Task", "List Tasks"], ["Schedule Tasks", "Brainstorm Ideas"], ["Back"]],
    one_time_keyboard=True
)
