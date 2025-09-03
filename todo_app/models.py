from .extensions import db
from datetime import datetime, timezone
from typing import Optional


class Todo(db.Model):
    """
    Model for the Todo entity.
    """

    __tablename__ = "todos"

    id = db.Column(db.Integer, primary_key=True)
    judul = db.Column(db.String(255), nullable=False, unique=True)  # Title of the task
    status = db.Column(db.Boolean, default=False, nullable=False)  # Completed or not
    prioritas = db.Column(
        db.String(10), default="Medium", nullable=False
    )  # Priority: High/Medium/Low
    deadline = db.Column(db.Date, nullable=True)  # Deadline date

    created_at = db.Column(
        db.DateTime, default=lambda: datetime.now(timezone.utc), nullable=False
    )
    updated_at = db.Column(db.DateTime, onupdate=lambda: datetime.now(timezone.utc))

    def __repr__(self) -> str:
        """
        String representation for debugging.
        """
        return f"<Todo {self.judul}>"
