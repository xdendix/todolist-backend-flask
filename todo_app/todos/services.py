"""
Service layer for Todo business logic.
Handles all CRUD operations and business rules.
"""
import logging
from typing import Dict, Any, List, Optional, Tuple
from ..extensions import db
from ..models import Todo
from ..schemas import TodoSchema
from ..constants import (
    DEFAULT_PAGE, DEFAULT_PER_PAGE, MAX_PER_PAGE,
    ERROR_MESSAGES, PRIORITIES
)

logger = logging.getLogger(__name__)

todo_schema = TodoSchema(session=db.session)
todos_schema = TodoSchema(many=True, session=db.session)


class TodoService:
    """Service class for Todo operations."""

    @staticmethod
    def validate_pagination_params(page: Optional[str], per_page: Optional[str]) -> Tuple[int, int]:
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

    @staticmethod
    def get_all_todos(page: int = DEFAULT_PAGE, per_page: int = DEFAULT_PER_PAGE) -> Dict[str, Any]:
        """
        Get paginated list of all todos.
        """
        pagination = Todo.query.order_by(Todo.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        todos_data = todos_schema.dump(pagination.items)
        logger.info(f"Retrieved {len(todos_data)} todos (page {page}, per_page {per_page})")

        return {
            "todos": todos_data,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }
        }

    @staticmethod
    def get_todo_by_id(todo_id: int) -> Todo:
        """
        Get a single todo by ID.
        Raises ValueError if not found.
        """
        try:
            todo = db.get_or_404(Todo, todo_id)
            logger.info(f"Retrieved todo {todo_id}")
            return todo
        except Exception:
            logger.warning(f"Todo {todo_id} not found")
            raise ValueError(ERROR_MESSAGES["todo_not_found"])

    @staticmethod
    def create_todo(data: Dict[str, Any]) -> Todo:
        """
        Create a new todo.
        Validates data and checks for duplicates.
        """
        # Validate required fields
        if not data:
            raise ValueError(ERROR_MESSAGES["no_input"])

        # Check for duplicate title
        if "judul" in data:
            existing_todo = Todo.query.filter_by(judul=data["judul"]).first()
            if existing_todo:
                raise ValueError(ERROR_MESSAGES["duplicate_title"])

        # Load and validate data
        todo = todo_schema.load(data)

        # Save to database
        db.session.add(todo)
        db.session.commit()

        logger.info(f"Created todo: {todo.judul}")
        return todo

    @staticmethod
    def update_todo(todo_id: int, data: Dict[str, Any]) -> Todo:
        """
        Update an existing todo.
        """
        if not data:
            raise ValueError(ERROR_MESSAGES["no_data_for_update"])

        try:
            todo = db.get_or_404(Todo, todo_id)
        except Exception:
            logger.warning(f"Todo {todo_id} not found for update")
            raise ValueError(ERROR_MESSAGES["todo_not_found"])

        # Load and validate update data
        updated_todo = todo_schema.load(data, instance=todo, partial=True)

        # Commit changes
        db.session.commit()

        logger.info(f"Updated todo {todo_id}")
        return updated_todo

    @staticmethod
    def delete_todo(todo_id: int) -> None:
        """
        Delete a todo by ID.
        """
        try:
            todo = db.get_or_404(Todo, todo_id)
        except Exception:
            logger.warning(f"Todo {todo_id} not found for deletion")
            raise ValueError(ERROR_MESSAGES["todo_not_found"])

        db.session.delete(todo)
        db.session.commit()

        logger.info(f"Deleted todo {todo_id}")

    @staticmethod
    def search_todos(
        query: str = "",
        priority: str = "",
        status: str = "",
        deadline: str = "",
        deadline_from: str = "",
        deadline_to: str = "",
        page: int = DEFAULT_PAGE,
        per_page: int = DEFAULT_PER_PAGE
    ) -> Dict[str, Any]:
        """
        Search todos with filters.
        """
        base_query = Todo.query

        # Apply filters
        if query:
            base_query = base_query.filter(Todo.judul.ilike(f"%{query}%"))

        if priority and priority.capitalize() in PRIORITIES:
            base_query = base_query.filter_by(prioritas=priority.capitalize())

        if status.lower() in ["completed", "selesai"]:
            base_query = base_query.filter_by(status=True)
        elif status.lower() in ["pending", "belum"]:
            base_query = base_query.filter_by(status=False)

        if deadline:
            base_query = base_query.filter_by(deadline=deadline)

        if deadline_from:
            base_query = base_query.filter(Todo.deadline >= deadline_from)

        if deadline_to:
            base_query = base_query.filter(Todo.deadline <= deadline_to)

        # Paginate results
        pagination = base_query.order_by(Todo.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        results_data = todos_schema.dump(pagination.items)
        logger.info(f"Search returned {len(results_data)} todos (page {page}, per_page {per_page})")

        return {
            "todos": results_data,
            "pagination": {
                "page": pagination.page,
                "per_page": pagination.per_page,
                "total": pagination.total,
                "pages": pagination.pages,
                "has_next": pagination.has_next,
                "has_prev": pagination.has_prev,
            }
        }
