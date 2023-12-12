from telegram import ReplyKeyboardMarkup

# Define command stages for the 'Plan' conversation
CHOOSE_PLAN_TASK, TASK_INFO, SCHEDULE_TASK, CUSTOM_DATE, SCHEDULE_TASK_DATE,BACK_TO_MAIN_MENU = map(chr, range(6))

# Define keyboards for the 'Plan' conversation
plan_keyboard = ReplyKeyboardMarkup(
    [["Add Task", "List Tasks"], ["Schedule Tasks", "Brainstorm Ideas"], ["Back"]],
    one_time_keyboard=True
)

schedule_keyboard = ReplyKeyboardMarkup(
        [["Today", "Tomorrow"], ["Next week", "Custom date"], ["Skip", "Stop Scheduling"]],
        one_time_keyboard=True
    )