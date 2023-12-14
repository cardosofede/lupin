from telegram import ReplyKeyboardMarkup

schedule_keyboard = ReplyKeyboardMarkup(
        [["Today", "Tomorrow"], ["Next week", "Custom date"], ["Skip", "Stop Scheduling"]],
        one_time_keyboard=True
    )
