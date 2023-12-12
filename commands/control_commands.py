from telegram import ReplyKeyboardMarkup

# Define command stages for the 'Control' conversation
CHOOSE_CONTROL_TASK, REVIEW_OVERDUE, REVIEW_TODAY, EDIT_TASK, DELETE_TASK, ANALYZE_CONTROL = map(chr, range(6))

# Define keyboard for the 'Control' conversation
control_keyboard = ReplyKeyboardMarkup(
    [["Review Overdue Tasks", "Review Today's Tasks"],
     ["Edit Tasks", "Analyze & Control"],
     ["Delete Tasks", "Back"]],
    one_time_keyboard=True
)
