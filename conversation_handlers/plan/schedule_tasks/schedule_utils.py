import datetime


def get_later_this_week_date():
    """Calculate a date later this week."""
    today = datetime.datetime.now()
    days_to_weekend = 6 - today.weekday()  # Days until Sunday
    later_this_week = today + datetime.timedelta(
        days=min(2, days_to_weekend)
    )  # Assuming "later this week" means in the next 2 days or until Sunday
    return later_this_week


def get_next_week_date():
    """Calculate a date for next week."""
    today = datetime.datetime.now()
    next_week = today + datetime.timedelta(
        days=7 - today.weekday()
    )  # Start of next week (Monday)
    return next_week


def is_valid_date(date_str):
    """Check if the provided string is a valid date in YYYY-MM-DD format."""
    try:
        datetime.datetime.strptime(date_str, "%d-%m-%Y")
        return True
    except ValueError:
        return False


def update_task_in_list(tasks_list, updated_task):
    """
    Update a task in the tasks list with its new details.

    Args:
        tasks_list (List[Task]): The list of Task objects.
        updated_task (Task): The Task object with updated details.
    """
    for i, task in enumerate(tasks_list):
        if task.id == updated_task.id and task.task == updated_task.task:
            tasks_list[i] = updated_task
            break


def remove_task_from_list(tasks_list, task_to_remove):
    """
    Remove a task from the tasks list.

    Args:
        tasks_list (List[Task]): The list of Task objects.
        task_to_remove (Task): The Task object to remove.
    """
    for i, task in enumerate(tasks_list):
        if task.id == task_to_remove.id and task.task == task_to_remove.task:
            tasks_list.pop(i)
            break
