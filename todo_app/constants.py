"""
Constants for the Todo application.
Centralized definitions for messages, values, and limits to ensure consistency.
"""

# Priority levels
PRIORITIES = ["High", "Medium", "Low"]

# Status values (for clarity, though stored as bool in DB)
STATUS_COMPLETED = True
STATUS_PENDING = False

# Pagination limits
DEFAULT_PAGE = 1
DEFAULT_PER_PAGE = 10
MAX_PER_PAGE = 100

# Error messages
ERROR_MESSAGES = {
    "no_input": "No input provided.",
    "duplicate_title": "Title already exists, please use a different title.",
    "no_data_for_update": "No data provided for update.",
    "invalid_priority": "Priority must be High, Medium, or Low.",
    "invalid_deadline": "Invalid deadline format (use YYYY-MM-DD).",
    "empty_title": "Title cannot be empty.",
    "todo_not_found": "Todo not found.",
    "invalid_page": "Invalid page number.",
    "invalid_per_page": "Invalid per_page value.",
    "invalid_date": "Invalid date format.",
}

# Success messages
SUCCESS_MESSAGES = {
    "todo_created": "Todo created successfully.",
    "todo_updated": "Todo updated successfully.",
    "todo_deleted": "Todo deleted successfully.",
}

# Response keys
RESPONSE_SUCCESS = "success"
RESPONSE_MESSAGE = "message"
RESPONSE_DATA = "data"
RESPONSE_COUNT = "count"
RESPONSE_PAGINATION = "pagination"
