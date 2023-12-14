import datetime
from typing import List

from pydantic import BaseModel


class Task(BaseModel):
    task: str
    description: str = ""
    date_created: datetime.datetime = datetime.datetime.now()
    tags: list[str] = []
    date_scheduled: datetime.datetime = None
    priority: str = ""
    is_completed: bool = False

    @classmethod
    def create_simple_task(cls, task_name: str):
        """Create a task with just a name."""
        return cls(task=task_name)

    @classmethod
    def create_multiple_tasks(cls, user_input: str):
        """Create multiple tasks from user input."""
        task_lines = [line.strip("-*. ") for line in user_input.split('\n') if line.strip("-*. ")]
        return [cls(task=line) for line in task_lines]

    @classmethod
    def create_full_task(cls, user_input: str):
        """Create a full task with details from user input."""
        lines = user_input.split('\n')
        return cls(
            task=lines[0].strip(),
            description=lines[1].strip() if len(lines) > 1 else "",
            tags=cls.extract_tags(lines[2]) if len(lines) > 2 else [],
            date_scheduled=cls.parse_date(lines[3].strip()) if len(lines) > 3 else None,
            priority=lines[4].strip() if len(lines) > 4 else "",
        )

    @staticmethod
    def extract_tags(tag_line: str):
        """Extract tags from a line of text."""
        return [tag.strip() for tag in tag_line.split(',')]

    @staticmethod
    def parse_date(date_str: str):
        """Parse date string to datetime object."""
        return datetime.datetime.strptime(date_str, "%Y-%m-%d") if date_str else None

    def add_date_to_history(self, new_date: str):
        """Add a date to the task's scheduling history."""
        if not self.date_history:
            self.date_history.append(self.date_scheduled)
        self.date_scheduled = datetime.datetime.strptime(new_date, "%Y-%m-%d")
        self.date_history.append(self.date_scheduled)

    @staticmethod
    def format_task_summaries(tasks: List['Task']):
        """Format task summaries for display."""
        summaries = []
        for task in tasks:
            symbol = "✅" if task.is_completed else "🟥"
            summary = f"{symbol} *{task.task}*"
            summaries.append(summary)
        return "\n".join(summaries)

    @classmethod
    def categorize_tasks_by_schedule(cls, tasks: List['Task']):
        """Categorize tasks by their scheduled date."""
        now = datetime.datetime.now()
        today = now.date()
        end_of_week = today + datetime.timedelta(days=6 - today.weekday())

        not_scheduled, scheduled_today, scheduled_week, overdue = [], [], [], []
        for task in tasks:
            if task.date_scheduled:
                date_scheduled = task.date_scheduled.date()
                if date_scheduled < today and not task.is_completed:
                    overdue.append(task)
                elif date_scheduled == today:
                    scheduled_today.append(task)
                elif today < date_scheduled <= end_of_week:
                    scheduled_week.append(task)
            else:
                not_scheduled.append(task)
        return not_scheduled, scheduled_today, scheduled_week, overdue
