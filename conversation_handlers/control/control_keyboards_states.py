from telegram import ReplyKeyboardMarkup

# TODO: Evaluate to manage the states with Enums
# Define command stages for the 'Control' conversation
CHOOSE_CONTROL_TASK = map(chr, range(1))

(
    SELECT_OVERDUE_TASK,
    REVIEW_OVERDUE,
    SELECT_TODAY_TASK,
    REVIEW_TODAY,
    EDIT_TASK,
    DELETE_TASK,
    ANALYZE_CONTROL,
) = map(chr, range(2, 9))

# Define keyboard for the 'Control' conversation
control_keyboard = ReplyKeyboardMarkup(
    [
        ["Review Overdue Tasks", "Review Today's Tasks"],
        ["Edit Tasks", "Analyze & Control"],
        ["Back"],
    ],
    one_time_keyboard=True,
)

# Define keyboard for the 'Review Overdue Tasks' conversation
review_overdue_keyboard = ReplyKeyboardMarkup(
    [
        ["Complete", "Delete Task"],
        ["Reschedule for Tomorrow", "Reschedule for Next Week"],
        ["Skip", "Stop Review"],
    ],
    one_time_keyboard=True,
)
