"""
Middleware for request validation, logging, and security.
"""
import logging
import time
from functools import wraps
from flask import request, g
from typing import Callable, Any
from ..constants import ERROR_MESSAGES

logger = logging.getLogger(__name__)


def log_request_response(f: Callable) -> Callable:
    """
    Decorator to log request and response details.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # Log request
        start_time = time.time()
        g.request_start_time = start_time

        logger.info(f"Request: {request.method} {request.path} from {request.remote_addr}")

        # Call the actual function
        response = f(*args, **kwargs)

        # Log response
        duration = time.time() - start_time
        logger.info(".3f")

        return response

    return decorated_function


def validate_content_type(content_types: list[str] | None = None) -> Callable:
    """
    Decorator to validate request content type.
    """
    if content_types is None:
        content_types = ['application/json']

    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                content_type = request.headers.get('Content-Type', '').lower()
                if not any(ct in content_type for ct in content_types):
                    logger.warning(f"Invalid content type: {content_type}")
                    return {
                        "success": False,
                        "message": ERROR_MESSAGES["invalid_content_type"]
                    }, 400
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def sanitize_input(data: dict) -> dict:
    """
    Sanitize input data by trimming whitespace and basic validation.
    """
    if not isinstance(data, dict):
        return data

    sanitized = {}
    for key, value in data.items():
        if isinstance(value, str):
            sanitized[key] = value.strip()
        elif isinstance(value, dict):
            sanitized[key] = sanitize_input(value)
        else:
            sanitized[key] = value

    return sanitized


def require_json_data(f: Callable) -> Callable:
    """
    Decorator to ensure JSON data is provided for POST/PUT/PATCH requests.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.method in ['POST', 'PUT', 'PATCH']:
            try:
                json_data = request.get_json()
                if json_data is None:
                    logger.warning("No JSON data provided")
                    return {
                        "success": False,
                        "message": ERROR_MESSAGES["no_input"]
                    }, 400

                # Sanitize the input
                sanitized_data = sanitize_input(json_data)
                g.json_data = sanitized_data

            except Exception as e:
                logger.warning(f"Invalid JSON data: {e}")
                return {
                    "success": False,
                    "message": ERROR_MESSAGES["invalid_json"]
                }, 400

            # Ensure empty body returns no_input error
            if json_data == {}:
                return {
                    "success": False,
                    "message": ERROR_MESSAGES["no_input"]
                }, 400

        return f(*args, **kwargs)
    return decorated_function


def add_security_headers(response):
    """
    Add security headers to the response.
    """
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response
