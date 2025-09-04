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

# HTTP Status Codes
HTTP_STATUS = {
    "OK": 200,
    "CREATED": 201,
    "NO_CONTENT": 204,
    "BAD_REQUEST": 400,
    "UNAUTHORIZED": 401,
    "FORBIDDEN": 403,
    "NOT_FOUND": 404,
    "METHOD_NOT_ALLOWED": 405,
    "CONFLICT": 409,
    "UNPROCESSABLE_ENTITY": 422,
    "INTERNAL_SERVER_ERROR": 500,
}

# Error messages
ERROR_MESSAGES = {
    "no_input": "No input provided.",
    "duplicate_title": "Judul sudah ada, silakan gunakan judul yang berbeda.",
    "no_data_for_update": "No data provided for update.",
    "invalid_priority": "Priority must be High, Medium, or Low.",
    "invalid_deadline": "Invalid deadline format (use YYYY-MM-DD).",
    "empty_title": "Title cannot be empty.",
    "todo_not_found": "Todo not found.",
    "invalid_page": "Invalid page number.",
    "invalid_per_page": "Invalid per_page value.",
    "invalid_date": "Invalid date format.",
    "validation_error": "Validation failed.",
    "database_error": "Database operation failed.",
    "internal_error": "Internal server error.",
    "invalid_content_type": "Invalid content type. Expected application/json.",
    "invalid_json": "Invalid JSON format.",
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
