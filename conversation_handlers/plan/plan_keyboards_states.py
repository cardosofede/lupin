from telegram import ReplyKeyboardMarkup

# Define command stages for the 'Plan' conversation
CHOOSE_PLAN_TASK = map(chr, range(1))

# Define command stages for the 'Add Task' conversation
TASK_INFO, ADD_TASK = map(chr, range(2, 4))

# Define command stages for the 'Schedule Tasks' conversation
SCHEDULE_TASK, SCHEDULE_TASK_DATE, CUSTOM_DATE = map(chr, range(5, 8))

# Define keyboards for the 'Plan' conversation
plan_keyboard = ReplyKeyboardMarkup(
    [["Add Task", "List Tasks"], ["Schedule Tasks", "Brainstorm Ideas"], ["Back"]],
    one_time_keyboard=True,
)

schedule_keyboard = ReplyKeyboardMarkup(
    [["Today", "Tomorrow"], ["Next week", "Custom date"], ["Skip", "Stop Scheduling"]],
    one_time_keyboard=True,
)
