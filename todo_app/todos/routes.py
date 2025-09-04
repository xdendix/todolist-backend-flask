import logging
from flask import Blueprint, request, jsonify, current_app
from flask_restx import Resource
from ..extensions import db
from ..models import Todo
from ..schemas import TodoSchema
from ..api_docs import todos_ns
from ..constants import (
    DEFAULT_PAGE, DEFAULT_PER_PAGE, MAX_PER_PAGE,
    ERROR_MESSAGES, SUCCESS_MESSAGES,
    RESPONSE_SUCCESS, RESPONSE_MESSAGE, RESPONSE_DATA, RESPONSE_COUNT, RESPONSE_PAGINATION,
    PRIORITIES, HTTP_STATUS
)
from marshmallow import ValidationError
from typing import Dict, Any, Optional
from .services import TodoService
from .middleware import log_request_response, validate_content_type, require_json_data, add_security_headers

bp = Blueprint("todos", __name__)

# Set up logger
logger = logging.getLogger(__name__)

todo_schema = TodoSchema(session=db.session)
todos_schema = TodoSchema(many=True, session=db.session)


def build_pagination_response(
    items: Any,
    pagination_obj: Any,
    success: bool = True,
    message: Optional[str] = None
) -> Dict[str, Any]:
    """
    Build a standardized pagination response.
    """
    response = {
        RESPONSE_SUCCESS: success,
        RESPONSE_COUNT: len(items),
        RESPONSE_DATA: items,
        RESPONSE_PAGINATION: {
            "page": pagination_obj.page,
            "per_page": pagination_obj.per_page,
            "total": pagination_obj.total,
            "pages": pagination_obj.pages,
            "has_next": pagination_obj.has_next,
            "has_prev": pagination_obj.has_prev,
        }
    }
    if message:
        response[RESPONSE_MESSAGE] = message
    return response


# Centralized error handler
@bp.app_errorhandler(ValidationError)
def handle_validation_error(error):
    logger.warning(f"Validation error: {error.messages}")
    response = {
        RESPONSE_SUCCESS: False,
        RESPONSE_MESSAGE: ERROR_MESSAGES["validation_error"],
        "errors": error.messages
    }
    return jsonify(response), HTTP_STATUS["BAD_REQUEST"]


@bp.app_errorhandler(404)
def handle_404_error(error):
    logger.warning(f"Not found: {error}")
    response = {
        RESPONSE_SUCCESS: False,
        RESPONSE_MESSAGE: ERROR_MESSAGES["todo_not_found"]
    }
    return jsonify(response), HTTP_STATUS["NOT_FOUND"]


@bp.app_errorhandler(500)
def handle_500_error(error):
    logger.error(f"Internal server error: {error}")
    response = {
        RESPONSE_SUCCESS: False,
        RESPONSE_MESSAGE: ERROR_MESSAGES["internal_error"]
    }
    return jsonify(response), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


# Get all todos
@bp.route("/", methods=["GET"])
@todos_ns.doc('list_todos',
    responses={
        200: 'Success - Returns paginated list of todos',
        400: 'Bad Request - Invalid pagination parameters'
    },
    params={
        'page': {'description': 'Page number (default: 1)', 'type': 'integer', 'default': 1},
        'per_page': {'description': 'Items per page (default: 10, max: 100)', 'type': 'integer', 'default': 10}
    })
def list_todos():
    """
    Get list of all todos, ordered by creation time descending.
    Response body ordered with id first and timestamps last.
    Supports pagination with query parameters page and per_page.
    """
    try:
        page, per_page = TodoService.validate_pagination_params(
            request.args.get("page"), request.args.get("per_page")
        )
    except ValueError as e:
        logger.warning(f"Invalid pagination params: {e}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: str(e)}), HTTP_STATUS["BAD_REQUEST"]

    result = TodoService.get_all_todos(page=page, per_page=per_page)

    # Create a simple object to mimic pagination object
    class PaginationObj:
        def __init__(self, pagination_data):
            self.page = pagination_data["page"]
            self.per_page = pagination_data["per_page"]
            self.total = pagination_data["total"]
            self.pages = pagination_data["pages"]
            self.has_next = pagination_data["has_next"]
            self.has_prev = pagination_data["has_prev"]

    pagination_obj = PaginationObj(result["pagination"])
    response = build_pagination_response(result["todos"], pagination_obj)

    return jsonify(response), HTTP_STATUS["OK"]


# Create new todo
@bp.route("/", methods=["POST"])
@todos_ns.doc('create_todo',
    responses={
        201: 'Created - Todo successfully created',
        400: 'Bad Request - Invalid input data or duplicate title',
        500: 'Internal Server Error - Database error'
    },
    body=todos_ns.models['Todo'])
@validate_content_type()
@require_json_data
@log_request_response
def create_todo():
    """
    Create a new todo based on the JSON data sent.
    """
    json_data = request.get_json()
    if not json_data:
        logger.warning("No input provided for create todo")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["no_input"]}), HTTP_STATUS["BAD_REQUEST"]

    try:
        todo = TodoService.create_todo(json_data)
        current_app.logger.info(f"Created todo: {todo.judul}")
        todo_data = todo_schema.dump(todo)
        return jsonify(todo_data), HTTP_STATUS["CREATED"]
    except ValueError as ve:
        logger.warning(f"Validation error in create todo: {ve}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: str(ve)}), HTTP_STATUS["BAD_REQUEST"]
    except ValidationError as err:
        logger.warning(f"Validation error in create todo: {err.messages}")
        return jsonify(err.messages), HTTP_STATUS["BAD_REQUEST"]
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating todo: {e}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["database_error"]}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


# Get todo by ID
@bp.route("/<int:todo_id>", methods=["GET"])
@todos_ns.doc('get_todo',
    responses={
        200: 'Success - Returns todo data',
        404: 'Not Found - Todo with specified ID not found'
    },
    params={
        'todo_id': {'description': 'Todo ID', 'type': 'integer', 'required': True}
    })
def get_todo(todo_id: int):
    """
    Get todo by ID.
    """
    try:
        todo = TodoService.get_todo_by_id(todo_id)
        result = todo_schema.dump(todo)
        current_app.logger.info(f"Retrieved todo: {todo_id}")
        return jsonify(result), HTTP_STATUS["OK"]
    except Exception as e:
        logger.warning(f"Todo not found: {todo_id}")
        response = {
            RESPONSE_SUCCESS: False,
            RESPONSE_MESSAGE: ERROR_MESSAGES["todo_not_found"]
        }
        return jsonify(response), HTTP_STATUS["NOT_FOUND"]


# Update todo (PUT/PATCH)
@bp.route("/<int:todo_id>", methods=["PUT", "PATCH"])
@todos_ns.doc('update_todo',
    responses={
        200: 'Success - Todo successfully updated',
        400: 'Bad Request - Invalid input data or no data provided',
        404: 'Not Found - Todo with specified ID not found',
        500: 'Internal Server Error - Database error'
    },
    params={
        'todo_id': {'description': 'Todo ID', 'type': 'integer', 'required': True}
    },
    body=todos_ns.models['Todo'])
@validate_content_type()
@require_json_data
@log_request_response
def update_todo(todo_id: int):
    """
    Update todo by ID with JSON data sent.
    """
    json_data = request.get_json() or {}

    # Check if at least one field is provided for update
    if not json_data:
        logger.warning(f"No data provided for update: {todo_id}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["no_data_for_update"]}), HTTP_STATUS["BAD_REQUEST"]

    try:
        updated = TodoService.update_todo(todo_id, json_data)
        current_app.logger.info(f"Updated todo: {todo_id}")
        updated_data = todo_schema.dump(updated)
        return jsonify(updated_data), HTTP_STATUS["OK"]
    except ValueError as ve:
        if "not found" in str(ve).lower():
            logger.warning(f"Todo {todo_id} not found for update")
            return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: str(ve)}), HTTP_STATUS["NOT_FOUND"]
        else:
            logger.warning(f"Validation error in update todo {todo_id}: {ve}")
            return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: str(ve)}), HTTP_STATUS["BAD_REQUEST"]
    except ValidationError as err:
        logger.warning(f"Validation error in update todo {todo_id}: {err.messages}")
        return jsonify(err.messages), HTTP_STATUS["BAD_REQUEST"]
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating todo {todo_id}: {e}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["database_error"]}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


# Delete todo by ID
@bp.route("/<int:todo_id>", methods=["DELETE"])
@todos_ns.doc('delete_todo',
    responses={
        204: 'No Content - Todo successfully deleted',
        404: 'Not Found - Todo with specified ID not found',
        500: 'Internal Server Error - Database error'
    },
    params={
        'todo_id': {'description': 'Todo ID', 'type': 'integer', 'required': True}
    })
def delete_todo(todo_id: int):
    """
    Delete todo by ID.
    """
    try:
        TodoService.delete_todo(todo_id)
        current_app.logger.info(f"Deleted todo: {todo_id}")
        return "", HTTP_STATUS["NO_CONTENT"]
    except ValueError as ve:
        if "not found" in str(ve).lower():
            logger.warning(f"Todo {todo_id} not found for deletion")
            return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: str(ve)}), HTTP_STATUS["NOT_FOUND"]
        else:
            logger.warning(f"Delete error: {ve}")
            return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: str(ve)}), HTTP_STATUS["BAD_REQUEST"]
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting todo {todo_id}: {e}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["database_error"]}), HTTP_STATUS["INTERNAL_SERVER_ERROR"]


# Search todos with filters
@bp.route("/search", methods=["GET"])
@todos_ns.doc('search_todos',
    responses={
        200: 'Success - Returns filtered and paginated list of todos',
        400: 'Bad Request - Invalid search parameters'
    },
    params={
        'q': {'description': 'Search keyword in title (case insensitive)', 'type': 'string'},
        'prioritas': {'description': 'Filter by priority (High/Medium/Low)', 'type': 'string', 'enum': ['High', 'Medium', 'Low']},
        'status': {'description': 'Filter by status (completed/pending)', 'type': 'string', 'enum': ['completed', 'pending']},
        'deadline': {'description': 'Filter by exact deadline (YYYY-MM-DD)', 'type': 'string'},
        'deadline_from': {'description': 'Filter by deadline from date (YYYY-MM-DD)', 'type': 'string'},
        'deadline_to': {'description': 'Filter by deadline to date (YYYY-MM-DD)', 'type': 'string'},
        'page': {'description': 'Page number (default: 1)', 'type': 'integer', 'default': 1},
        'per_page': {'description': 'Items per page (default: 10, max: 100)', 'type': 'integer', 'default': 10}
    })
def search_todo():
    """
    Search todos based on query parameters:
    - q: title keyword (case insensitive)
    - prioritas: High, Medium, Low
    - status: completed, pending
    - deadline: exact deadline date (YYYY-MM-DD)
    - deadline_from: deadline from date (YYYY-MM-DD)
    - deadline_to: deadline to date (YYYY-MM-DD)
    """
    kata_kunci = request.args.get("q", "").lower()
    prioritas = request.args.get("prioritas", "").capitalize()
    status = request.args.get("status", "").lower()
    deadline = request.args.get("deadline", "")
    deadline_from = request.args.get("deadline_from", "")
    deadline_to = request.args.get("deadline_to", "")

    try:
        page, per_page = TodoService.validate_pagination_params(
            request.args.get("page"), request.args.get("per_page")
        )
    except ValueError as e:
        logger.warning(f"Invalid pagination params in search: {e}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: str(e)}), HTTP_STATUS["BAD_REQUEST"]

    result = TodoService.search_todos(
        query=kata_kunci,
        priority=prioritas,
        status=status,
        deadline=deadline,
        deadline_from=deadline_from,
        deadline_to=deadline_to,
        page=page,
        per_page=per_page
    )

    # Create a simple object to mimic pagination object
    class PaginationObj:
        def __init__(self, pagination_data):
            self.page = pagination_data["page"]
            self.per_page = pagination_data["per_page"]
            self.total = pagination_data["total"]
            self.pages = pagination_data["pages"]
            self.has_next = pagination_data["has_next"]
            self.has_prev = pagination_data["has_prev"]

    pagination_obj = PaginationObj(result["pagination"])
    response = build_pagination_response(result["todos"], pagination_obj)

    current_app.logger.info(f"Searched todos: page {page}, per_page {per_page}, count {len(result['todos'])}")
    return jsonify(response), HTTP_STATUS["OK"]
