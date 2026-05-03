import re
import uuid
from datetime import datetime
from typing import Optional

def generate_slug(text: str) -> str:
    slug = text.lower().strip()
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[\s_-]+', '-', slug)
    slug = re.sub(r'^-+|-+$', '', slug)
    return slug + "-" + str(uuid.uuid4())[:8]

def validate_email(email: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    if dt is None:
        return ""
    return dt.strftime(format_str)

def calculate_completion_percentage(total: int, completed: int) -> float:
    if total == 0:
        return 0.0
    return round((completed / total) * 100, 2)

def truncate_text(text: str, max_length: int = 100) -> str:
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."

def is_overdue(due_date: Optional[datetime]) -> bool:
    if not due_date:
        return False
    return due_date < datetime.now()

__all__ = [
    'generate_slug', 'validate_email', 'format_datetime',
    'calculate_completion_percentage', 'truncate_text', 'is_overdue'
]
