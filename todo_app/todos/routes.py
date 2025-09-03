import logging
from flask import Blueprint, request, jsonify
from ..extensions import db
from ..models import Todo
from ..schemas import TodoSchema
from ..constants import (
    DEFAULT_PAGE, DEFAULT_PER_PAGE, MAX_PER_PAGE,
    ERROR_MESSAGES, SUCCESS_MESSAGES,
    RESPONSE_SUCCESS, RESPONSE_MESSAGE, RESPONSE_DATA, RESPONSE_COUNT, RESPONSE_PAGINATION,
    PRIORITIES
)
from marshmallow import ValidationError
from typing import Dict, Any, List, Optional

bp = Blueprint("todos", __name__)

# Set up logger
logger = logging.getLogger(__name__)

todo_schema = TodoSchema(session=db.session)
todos_schema = TodoSchema(many=True, session=db.session)


def validate_pagination_params(page: Optional[str], per_page: Optional[str]) -> tuple[int, int]:
    """
    Validate and sanitize pagination parameters.
    Returns (page, per_page) as integers.
    """
    try:
        page_int = int(page) if page else DEFAULT_PAGE
        per_page_int = int(per_page) if per_page else DEFAULT_PER_PAGE
    except ValueError:
        raise ValueError(ERROR_MESSAGES["invalid_page"])

    if page_int < 1:
        page_int = DEFAULT_PAGE
    if per_page_int > MAX_PER_PAGE:
        per_page_int = MAX_PER_PAGE
    if per_page_int < 1:
        per_page_int = DEFAULT_PER_PAGE

    return page_int, per_page_int


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


# Get all todos
@bp.route("/", methods=["GET"])
def list_todos():
    """
    Get list of all todos, ordered by creation time descending.
    Response body ordered with id first and timestamps last.
    Supports pagination with query parameters page and per_page.
    """
    try:
        page, per_page = validate_pagination_params(
            request.args.get("page"), request.args.get("per_page")
        )
    except ValueError as e:
        logger.warning(f"Invalid pagination params: {e}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: str(e)}), 400

    pagination = Todo.query.order_by(Todo.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    todos_data = todos_schema.dump(pagination.items)
    response = build_pagination_response(todos_data, pagination)

    logger.info(f"Listed todos: page {page}, per_page {per_page}, count {len(todos_data)}")
    return jsonify(response), 200


# Create new todo
@bp.route("/", methods=["POST"])
def create_todo():
    """
    Create a new todo based on the JSON data sent.
    """
    json_data = request.get_json()
    if not json_data:
        logger.warning("No input provided for create todo")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["no_input"]}), 400

    try:
        todo = todo_schema.load(json_data)
    except ValidationError as err:
        logger.warning(f"Validation error in create todo: {err.messages}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: err.messages}), 400

    # Check for duplicate title
    existing_todo = Todo.query.filter_by(judul=json_data.get("judul")).first()
    if existing_todo:
        logger.warning(f"Duplicate title: {json_data.get('judul')}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["duplicate_title"]}), 400

    try:
        db.session.add(todo)
        db.session.commit()
        logger.info(f"Created todo: {todo.judul}")
        return jsonify({RESPONSE_SUCCESS: True, RESPONSE_DATA: todo_schema.dump(todo)}), 201
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error creating todo: {e}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: "Internal server error"}), 500


# Get todo by ID
@bp.route("/<int:todo_id>", methods=["GET"])
def get_todo(todo_id: int):
    """
    Get todo by ID.
    """
    try:
        todo = db.get_or_404(Todo, todo_id)
        result = todo_schema.dump(todo)
        logger.info(f"Retrieved todo: {todo_id}")
        return jsonify({RESPONSE_SUCCESS: True, RESPONSE_DATA: result}), 200
    except Exception as e:
        logger.warning(f"Todo not found: {todo_id}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["todo_not_found"]}), 404


# Update todo (PUT/PATCH)
@bp.route("/<int:todo_id>", methods=["PUT", "PATCH"])
def update_todo(todo_id: int):
    """
    Update todo by ID with JSON data sent.
    """
    try:
        todo = db.get_or_404(Todo, todo_id)
    except Exception:
        logger.warning(f"Todo not found for update: {todo_id}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["todo_not_found"]}), 404

    json_data = request.get_json() or {}

    # Check if at least one field is provided for update
    if not json_data:
        logger.warning(f"No data provided for update: {todo_id}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["no_data_for_update"]}), 400

    try:
        updated = todo_schema.load(json_data, instance=todo, partial=True)
    except ValidationError as err:
        logger.warning(f"Validation error in update todo {todo_id}: {err.messages}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: err.messages}), 400

    try:
        db.session.commit()
        logger.info(f"Updated todo: {todo_id}")
        return jsonify({RESPONSE_SUCCESS: True, RESPONSE_DATA: todo_schema.dump(updated)}), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error updating todo {todo_id}: {e}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: "Internal server error"}), 500


# Delete todo by ID
@bp.route("/<int:todo_id>", methods=["DELETE"])
def delete_todo(todo_id: int):
    """
    Delete todo by ID.
    """
    try:
        todo = db.get_or_404(Todo, todo_id)
    except Exception:
        logger.warning(f"Todo not found for delete: {todo_id}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: ERROR_MESSAGES["todo_not_found"]}), 404

    try:
        db.session.delete(todo)
        db.session.commit()
        logger.info(f"Deleted todo: {todo_id}")
        return "", 204
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting todo {todo_id}: {e}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: "Internal server error"}), 500


# Search todos with filters
@bp.route("/search", methods=["GET"])
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
        page, per_page = validate_pagination_params(
            request.args.get("page"), request.args.get("per_page")
        )
    except ValueError as e:
        logger.warning(f"Invalid pagination params in search: {e}")
        return jsonify({RESPONSE_SUCCESS: False, RESPONSE_MESSAGE: str(e)}), 400

    query = Todo.query

    if kata_kunci:
        query = query.filter(Todo.judul.ilike(f"%{kata_kunci}%"))

    if prioritas in PRIORITIES:
        query = query.filter_by(prioritas=prioritas)

    if status == "completed":
        query = query.filter_by(status=True)
    elif status == "pending":
        query = query.filter_by(status=False)

    if deadline:
        query = query.filter_by(deadline=deadline)

    if deadline_from:
        query = query.filter(Todo.deadline >= deadline_from)

    if deadline_to:
        query = query.filter(Todo.deadline <= deadline_to)

    pagination = query.order_by(Todo.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    results_data = todos_schema.dump(pagination.items)
    response = build_pagination_response(results_data, pagination)

    logger.info(f"Searched todos: page {page}, per_page {per_page}, count {len(results_data)}")
    return jsonify(response), 200
