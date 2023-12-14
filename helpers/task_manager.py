import datetime

from telegram.ext import ContextTypes


def categorize_tasks_by_schedule(context: ContextTypes.DEFAULT_TYPE):
    """Categorize tasks by their scheduled date."""
    now = datetime.datetime.now()
    today = now.date()
    end_of_week = today + datetime.timedelta(days=6 - today.weekday())

    tasks = context.user_data.get('tasks', [])
    not_scheduled, scheduled_today, scheduled_week, overdue = [], [], [], []
    for task in tasks:
        date_scheduled = task.get('date_scheduled')
        if date_scheduled:
            date_scheduled = datetime.datetime.strptime(date_scheduled, "%Y-%m-%d").date()
            if date_scheduled < today and not task.get('is_completed'):
                overdue.append(task)
            elif date_scheduled == today:
                scheduled_today.append(task)
            elif today < date_scheduled <= end_of_week:
                scheduled_week.append(task)
        else:
            not_scheduled.append(task)
    return not_scheduled, scheduled_today, scheduled_week, overdue


def format_task_summaries(tasks: list[dict]):
    """Format task summaries for display."""
    summaries = []
    for task in tasks:
        symbol = "✅" if task.get('is_completed') else "🟥"
        summary = f"{symbol} *{task['task']}*"
        summaries.append(summary)
    return "\n".join(summaries)


def add_date_to_history(task, new_date):
    if 'date_history' not in task:
        task['date_history'] = [task.get('date_scheduled', '')]
    task['date_history'].append(new_date)
    task['date_scheduled'] = new_date